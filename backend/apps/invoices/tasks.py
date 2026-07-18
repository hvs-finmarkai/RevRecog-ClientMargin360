import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def generate_invoice(self, contract_id, period_start, period_end):
    try:
        from apps.contracts.models import Contract
        from apps.invoices.models import Invoice, InvoiceLineItem
        from apps.invoices.services.generator import InvoiceGenerator

        contract = Contract.objects.get(id=contract_id)

        generator = InvoiceGenerator()
        billable_items = generator.get_billable_items(
            contract=contract,
            period_start=period_start,
            period_end=period_end,
        )

        if not billable_items:
            return {
                "status": "skipped",
                "reason": "no_billable_items",
                "contract_id": str(contract_id),
            }

        with transaction.atomic():
            invoice = Invoice.objects.create(
                organization_id=contract.organization_id,
                contract=contract,
                client_name=contract.client_name,
                period_start=period_start,
                period_end=period_end,
                status="draft",
                due_date=generator.calculate_due_date(contract),
                currency=contract.currency,
            )

            subtotal = Decimal("0.00")
            for item in billable_items:
                line_item = InvoiceLineItem.objects.create(
                    invoice=invoice,
                    description=item["description"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    amount=item["quantity"] * item["unit_price"],
                    billable_type=item["type"],
                    billable_id=item.get("id"),
                )
                subtotal += line_item.amount

            tax_amount = generator.calculate_tax(subtotal, contract)
            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = subtotal + tax_amount
            invoice.save(update_fields=["subtotal", "tax_amount", "total_amount"])

            generator.mark_items_as_invoiced(billable_items, invoice)

        return {
            "status": "success",
            "invoice_id": str(invoice.id),
            "total_amount": str(invoice.total_amount),
            "line_items_count": len(billable_items),
        }

    except Contract.DoesNotExist:
        logger.error(f"Contract not found: {contract_id}")
        return {"status": "failed", "reason": "contract_not_found"}
    except Exception as exc:
        logger.exception(f"Error generating invoice for contract {contract_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    acks_late=True,
)
def bulk_generate_invoices(self, organization_id, period):
    try:
        from apps.contracts.models import Contract
        from apps.invoices.services.generator import InvoiceGenerator

        generator = InvoiceGenerator()
        period_start, period_end = generator.parse_period(period)

        active_contracts = Contract.objects.filter(
            organization_id=organization_id,
            status="active",
            billing_frequency__in=generator.get_matching_frequencies(period),
            start_date__lte=period_end,
            end_date__gte=period_start,
        )

        results = {
            "total_contracts": active_contracts.count(),
            "generated": 0,
            "skipped": 0,
            "failed": 0,
            "invoice_ids": [],
        }

        for contract in active_contracts:
            result = generate_invoice(
                str(contract.id),
                period_start.isoformat(),
                period_end.isoformat(),
            )

            if result["status"] == "success":
                results["generated"] += 1
                results["invoice_ids"].append(result["invoice_id"])
            elif result["status"] == "skipped":
                results["skipped"] += 1
            else:
                results["failed"] += 1

        return results

    except Exception as exc:
        logger.exception(f"Error in bulk invoice generation for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    acks_late=True,
)
def send_invoice_reminder(self, invoice_id):
    try:
        from apps.invoices.models import Invoice
        from apps.notifications.tasks import send_email_notification
        from apps.invoices.services.reminder import ReminderService

        invoice = Invoice.objects.select_related("contract").get(id=invoice_id)

        if invoice.status in ("paid", "cancelled"):
            return {
                "status": "skipped",
                "reason": f"invoice_status_{invoice.status}",
            }

        reminder_service = ReminderService()
        recipients = reminder_service.get_reminder_recipients(invoice)
        template_id = reminder_service.get_template(invoice)

        for recipient in recipients:
            send_email_notification.delay(
                user_id=str(recipient.id),
                template_id=template_id,
                context={
                    "invoice_number": invoice.invoice_number,
                    "amount": str(invoice.total_amount),
                    "due_date": invoice.due_date.isoformat(),
                    "client_name": invoice.client_name,
                    "days_overdue": (timezone.now().date() - invoice.due_date).days,
                },
            )

        invoice.last_reminder_sent = timezone.now()
        invoice.reminder_count += 1
        invoice.save(update_fields=["last_reminder_sent", "reminder_count"])

        return {
            "status": "success",
            "invoice_id": str(invoice_id),
            "recipients_count": len(recipients),
        }

    except Invoice.DoesNotExist:
        logger.error(f"Invoice not found: {invoice_id}")
        return {"status": "failed", "reason": "invoice_not_found"}
    except Exception as exc:
        logger.exception(f"Error sending reminder for invoice {invoice_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def check_overdue_invoices(self):
    try:
        from apps.invoices.models import Invoice
        from apps.notifications.tasks import send_notification

        now = timezone.now().date()

        newly_overdue = Invoice.objects.filter(
            due_date__lt=now,
            status="sent",
        ).exclude(
            status__in=["paid", "cancelled", "overdue"]
        )

        overdue_count = 0
        for invoice in newly_overdue:
            invoice.status = "overdue"
            invoice.save(update_fields=["status"])
            overdue_count += 1

            send_notification.delay(
                notification_type="invoice_overdue",
                organization_id=str(invoice.organization_id),
                context={
                    "invoice_id": str(invoice.id),
                    "invoice_number": invoice.invoice_number,
                    "client_name": invoice.client_name,
                    "amount": str(invoice.total_amount),
                    "due_date": invoice.due_date.isoformat(),
                    "days_overdue": (now - invoice.due_date).days,
                },
            )

        overdue_needing_reminder = Invoice.objects.filter(
            status="overdue",
            last_reminder_sent__lt=timezone.now() - timedelta(days=7),
            reminder_count__lt=5,
        )

        for invoice in overdue_needing_reminder:
            send_invoice_reminder.delay(str(invoice.id))

        return {
            "status": "completed",
            "newly_overdue": overdue_count,
            "reminders_queued": overdue_needing_reminder.count(),
        }

    except Exception as exc:
        logger.exception("Error checking overdue invoices")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}
