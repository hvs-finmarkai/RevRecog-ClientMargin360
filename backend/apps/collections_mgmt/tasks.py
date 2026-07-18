import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q, F

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def update_aging_buckets(self, organization_id):
    try:
        from apps.collections_mgmt.models import AgingBucket, AgingSummary
        from apps.invoices.models import Invoice

        today = timezone.now().date()

        outstanding_invoices = Invoice.objects.filter(
            organization_id=organization_id,
            status__in=["sent", "overdue"],
        ).exclude(total_amount__lte=F("paid_amount"))

        buckets = {
            "current": {"min": None, "max": 0, "total": Decimal("0"), "count": 0, "invoices": []},
            "1_30": {"min": 1, "max": 30, "total": Decimal("0"), "count": 0, "invoices": []},
            "31_60": {"min": 31, "max": 60, "total": Decimal("0"), "count": 0, "invoices": []},
            "61_90": {"min": 61, "max": 90, "total": Decimal("0"), "count": 0, "invoices": []},
            "90_plus": {"min": 91, "max": None, "total": Decimal("0"), "count": 0, "invoices": []},
        }

        for invoice in outstanding_invoices:
            outstanding_amount = invoice.total_amount - (invoice.paid_amount or Decimal("0"))
            days_outstanding = (today - invoice.due_date).days

            if days_outstanding <= 0:
                bucket_key = "current"
            elif days_outstanding <= 30:
                bucket_key = "1_30"
            elif days_outstanding <= 60:
                bucket_key = "31_60"
            elif days_outstanding <= 90:
                bucket_key = "61_90"
            else:
                bucket_key = "90_plus"

            buckets[bucket_key]["total"] += outstanding_amount
            buckets[bucket_key]["count"] += 1
            buckets[bucket_key]["invoices"].append(str(invoice.id))

        with transaction.atomic():
            AgingBucket.objects.filter(
                organization_id=organization_id,
            ).delete()

            for bucket_key, data in buckets.items():
                AgingBucket.objects.create(
                    organization_id=organization_id,
                    bucket_name=bucket_key,
                    total_amount=data["total"],
                    invoice_count=data["count"],
                    invoice_ids=data["invoices"],
                    as_of_date=today,
                )

            total_outstanding = sum(b["total"] for b in buckets.values())
            total_overdue = sum(
                b["total"] for k, b in buckets.items() if k != "current"
            )

            AgingSummary.objects.update_or_create(
                organization_id=organization_id,
                defaults={
                    "total_outstanding": total_outstanding,
                    "total_overdue": total_overdue,
                    "total_invoices": outstanding_invoices.count(),
                    "as_of_date": today,
                    "updated_at": timezone.now(),
                },
            )

        return {
            "status": "completed",
            "total_outstanding": str(total_outstanding),
            "total_overdue": str(total_overdue),
            "invoices_processed": outstanding_invoices.count(),
            "buckets": {k: {"total": str(v["total"]), "count": v["count"]} for k, v in buckets.items()},
        }

    except Exception as exc:
        logger.exception(f"Error updating aging buckets for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def send_dunning_reminders(self):
    try:
        from apps.collections_mgmt.models import DunningSchedule
        from apps.invoices.models import Invoice
        from apps.notifications.tasks import send_email_notification

        now = timezone.now()
        today = now.date()

        schedules = DunningSchedule.objects.filter(is_active=True)
        reminders_sent = 0

        for schedule in schedules:
            overdue_invoices = Invoice.objects.filter(
                organization_id=schedule.organization_id,
                status="overdue",
            ).exclude(
                total_amount__lte=F("paid_amount")
            )

            for invoice in overdue_invoices:
                days_overdue = (today - invoice.due_date).days

                if days_overdue not in schedule.reminder_days:
                    continue

                if invoice.last_reminder_sent and (
                    now - invoice.last_reminder_sent
                ).days < schedule.min_days_between_reminders:
                    continue

                template_id = schedule.get_template_for_days(days_overdue)

                recipients = schedule.get_recipients(invoice)
                for recipient in recipients:
                    send_email_notification.delay(
                        user_id=str(recipient.id),
                        template_id=template_id,
                        context={
                            "invoice_number": invoice.invoice_number,
                            "amount_due": str(
                                invoice.total_amount - (invoice.paid_amount or Decimal("0"))
                            ),
                            "due_date": invoice.due_date.isoformat(),
                            "days_overdue": days_overdue,
                            "client_name": invoice.client_name,
                            "organization_name": schedule.organization.name,
                        },
                    )

                invoice.last_reminder_sent = now
                invoice.reminder_count = (invoice.reminder_count or 0) + 1
                invoice.save(update_fields=["last_reminder_sent", "reminder_count"])
                reminders_sent += 1

        return {
            "status": "completed",
            "reminders_sent": reminders_sent,
        }

    except Exception as exc:
        logger.exception("Error sending dunning reminders")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def generate_cash_forecast(self, organization_id):
    try:
        from apps.collections_mgmt.models import CashForecast, CashForecastEntry
        from apps.collections_mgmt.services.forecaster import CashForecaster
        from apps.invoices.models import Invoice

        forecaster = CashForecaster()
        now = timezone.now()

        outstanding_invoices = Invoice.objects.filter(
            organization_id=organization_id,
            status__in=["sent", "overdue"],
        ).exclude(total_amount__lte=F("paid_amount"))

        historical_payments = forecaster.get_payment_history(organization_id)

        scenarios = {}
        for scenario in ["optimistic", "base", "pessimistic"]:
            projections = forecaster.project_collections(
                invoices=outstanding_invoices,
                payment_history=historical_payments,
                scenario=scenario,
                horizon_days=90,
            )
            scenarios[scenario] = projections

        with transaction.atomic():
            CashForecast.objects.filter(
                organization_id=organization_id,
                is_current=True,
            ).update(is_current=False)

            forecast = CashForecast.objects.create(
                organization_id=organization_id,
                generated_at=now,
                horizon_days=90,
                is_current=True,
                total_outstanding=sum(
                    i.total_amount - (i.paid_amount or Decimal("0"))
                    for i in outstanding_invoices
                ),
                optimistic_total=scenarios["optimistic"]["total"],
                base_total=scenarios["base"]["total"],
                pessimistic_total=scenarios["pessimistic"]["total"],
            )

            for scenario_name, projections in scenarios.items():
                for entry in projections["weekly_entries"]:
                    CashForecastEntry.objects.create(
                        forecast=forecast,
                        scenario=scenario_name,
                        week_start=entry["week_start"],
                        week_end=entry["week_end"],
                        projected_amount=entry["amount"],
                        probability=entry["probability"],
                        invoice_count=entry["invoice_count"],
                    )

        return {
            "status": "completed",
            "forecast_id": str(forecast.id),
            "outstanding_invoices": outstanding_invoices.count(),
            "base_projection": str(scenarios["base"]["total"]),
        }

    except Exception as exc:
        logger.exception(f"Error generating cash forecast for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def reconcile_payments(self, organization_id):
    try:
        from apps.collections_mgmt.models import PaymentReconciliation
        from apps.collections_mgmt.services.reconciler import PaymentReconciler
        from apps.invoices.models import Invoice, Payment

        reconciler = PaymentReconciler()

        unreconciled_payments = Payment.objects.filter(
            organization_id=organization_id,
            is_reconciled=False,
        )

        if not unreconciled_payments.exists():
            return {"status": "completed", "reconciled": 0, "unmatched": 0}

        reconciled_count = 0
        unmatched_count = 0
        results = []

        for payment in unreconciled_payments:
            match = reconciler.find_matching_invoice(payment)

            if match:
                with transaction.atomic():
                    invoice = match["invoice"]
                    invoice.paid_amount = (invoice.paid_amount or Decimal("0")) + payment.amount

                    if invoice.paid_amount >= invoice.total_amount:
                        invoice.status = "paid"
                        invoice.payment_date = payment.payment_date
                    else:
                        invoice.status = "partially_paid"

                    invoice.save(update_fields=["paid_amount", "status", "payment_date"])

                    payment.is_reconciled = True
                    payment.invoice = invoice
                    payment.reconciled_at = timezone.now()
                    payment.save(update_fields=["is_reconciled", "invoice", "reconciled_at"])

                    PaymentReconciliation.objects.create(
                        organization_id=organization_id,
                        payment=payment,
                        invoice=invoice,
                        matched_amount=payment.amount,
                        match_confidence=match["confidence"],
                        match_method=match["method"],
                        reconciled_at=timezone.now(),
                    )

                reconciled_count += 1
                results.append({
                    "payment_id": str(payment.id),
                    "invoice_id": str(invoice.id),
                    "amount": str(payment.amount),
                    "confidence": match["confidence"],
                })
            else:
                unmatched_count += 1

        return {
            "status": "completed",
            "reconciled": reconciled_count,
            "unmatched": unmatched_count,
            "total_processed": unreconciled_payments.count(),
            "details": results,
        }

    except Exception as exc:
        logger.exception(f"Error reconciling payments for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}
