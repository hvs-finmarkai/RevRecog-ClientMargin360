import logging
from datetime import timedelta

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
def parse_contract_document(self, document_id):
    try:
        from apps.contracts.models import ContractDocument, Contract
        from apps.contracts.services.ocr import OCRService
        from apps.contracts.services.nlp import NLPExtractor
        from apps.contracts.services.validation import EntityValidator

        document = ContractDocument.objects.get(id=document_id)
        document.status = "processing"
        document.save(update_fields=["status"])

        ocr_service = OCRService()
        raw_text = ocr_service.extract_text(document.file.path)

        if not raw_text or len(raw_text.strip()) < 50:
            document.status = "ocr_failed"
            document.error_message = "OCR produced insufficient text"
            document.save(update_fields=["status", "error_message"])
            return {"status": "failed", "reason": "ocr_insufficient_text"}

        nlp_extractor = NLPExtractor()
        entities = nlp_extractor.extract_entities(raw_text)

        validator = EntityValidator()
        validation_result = validator.validate(entities)

        confidence_score = validation_result.confidence_score

        with transaction.atomic():
            document.extracted_text = raw_text
            document.extracted_entities = entities
            document.confidence_score = confidence_score
            document.validation_issues = validation_result.issues

            if confidence_score >= 0.8:
                document.status = "completed"
                contract = Contract.objects.create(
                    organization_id=document.organization_id,
                    document=document,
                    **entities,
                )
            elif confidence_score >= 0.6:
                document.status = "review_required"
                contract = None
            else:
                document.status = "low_confidence"
                contract = None

            document.save()

        return {
            "status": document.status,
            "confidence_score": confidence_score,
            "contract_id": str(contract.id) if contract else None,
            "issues": validation_result.issues,
        }

    except ContractDocument.DoesNotExist:
        logger.error(f"Document not found: {document_id}")
        return {"status": "failed", "reason": "document_not_found"}
    except Exception as exc:
        logger.exception(f"Error parsing document {document_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            document = ContractDocument.objects.filter(id=document_id).first()
            if document:
                document.status = "failed"
                document.error_message = str(exc)
                document.save(update_fields=["status", "error_message"])
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def check_contract_compliance(self, contract_id):
    try:
        from apps.contracts.models import Contract, ComplianceCheck
        from apps.contracts.services.compliance import ASC606ComplianceChecker

        contract = Contract.objects.select_related("document").get(id=contract_id)

        checker = ASC606ComplianceChecker()
        result = checker.check(contract)

        compliance_check = ComplianceCheck.objects.create(
            contract=contract,
            organization_id=contract.organization_id,
            step1_identification=result.step1_passed,
            step2_obligations=result.step2_passed,
            step3_price=result.step3_passed,
            step4_allocation=result.step4_passed,
            step5_recognition=result.step5_passed,
            overall_compliant=result.is_compliant,
            issues=result.issues,
            recommendations=result.recommendations,
            checked_at=timezone.now(),
        )

        contract.is_compliant = result.is_compliant
        contract.last_compliance_check = timezone.now()
        contract.save(update_fields=["is_compliant", "last_compliance_check"])

        if not result.is_compliant:
            from apps.notifications.tasks import send_notification
            send_notification.delay(
                notification_type="compliance_issue",
                organization_id=str(contract.organization_id),
                context={
                    "contract_id": str(contract.id),
                    "client_name": contract.client_name,
                    "issues": result.issues,
                },
            )

        return {
            "contract_id": str(contract_id),
            "compliant": result.is_compliant,
            "issues_count": len(result.issues),
            "check_id": str(compliance_check.id),
        }

    except Contract.DoesNotExist:
        logger.error(f"Contract not found: {contract_id}")
        return {"status": "failed", "reason": "contract_not_found"}
    except Exception as exc:
        logger.exception(f"Error checking compliance for contract {contract_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def notify_contract_expiry(self):
    try:
        from apps.contracts.models import Contract
        from apps.notifications.tasks import send_notification

        now = timezone.now()
        expiry_windows = [
            (30, "expiring_30_days"),
            (14, "expiring_14_days"),
            (7, "expiring_7_days"),
        ]

        total_notified = 0

        for days, notification_type in expiry_windows:
            target_date = now + timedelta(days=days)
            window_start = target_date.replace(hour=0, minute=0, second=0)
            window_end = target_date.replace(hour=23, minute=59, second=59)

            expiring_contracts = Contract.objects.filter(
                end_date__gte=window_start,
                end_date__lte=window_end,
                status="active",
                expiry_notified_days__lt=days,
            ).select_related("organization")

            for contract in expiring_contracts:
                send_notification.delay(
                    notification_type=notification_type,
                    organization_id=str(contract.organization_id),
                    context={
                        "contract_id": str(contract.id),
                        "client_name": contract.client_name,
                        "end_date": contract.end_date.isoformat(),
                        "days_remaining": days,
                    },
                )
                contract.expiry_notified_days = days
                contract.save(update_fields=["expiry_notified_days"])
                total_notified += 1

        return {
            "status": "completed",
            "contracts_notified": total_notified,
        }

    except Exception as exc:
        logger.exception("Error in contract expiry notification task")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}
