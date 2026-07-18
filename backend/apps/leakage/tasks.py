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
def run_leakage_detection(self, organization_id):
    try:
        from apps.leakage.models import LeakageAlert, LeakageScan
        from apps.leakage.services.detector import LeakageDetector
        from apps.leakage.services.feature_engine import FeatureEngine
        from apps.notifications.tasks import send_notification

        scan = LeakageScan.objects.create(
            organization_id=organization_id,
            status="running",
            started_at=timezone.now(),
        )

        feature_engine = FeatureEngine()
        features = feature_engine.compute_features(organization_id)

        if features.empty:
            scan.status = "completed"
            scan.completed_at = timezone.now()
            scan.result_summary = {"alerts_generated": 0, "reason": "no_data"}
            scan.save()
            return {"status": "completed", "alerts": 0, "reason": "no_data"}

        detector = LeakageDetector()
        anomalies = detector.detect(features)
        rule_violations = detector.check_rules(features)

        combined_scores = detector.compute_composite_scores(anomalies, rule_violations)

        alerts_created = 0
        with transaction.atomic():
            for score_entry in combined_scores:
                if score_entry["score"] >= detector.alert_threshold:
                    LeakageAlert.objects.create(
                        organization_id=organization_id,
                        scan=scan,
                        client_id=score_entry["client_id"],
                        alert_type=score_entry["type"],
                        severity=score_entry["severity"],
                        score=score_entry["score"],
                        estimated_amount=score_entry["estimated_amount"],
                        evidence=score_entry["evidence"],
                        status="open",
                        detected_at=timezone.now(),
                    )
                    alerts_created += 1

            scan.status = "completed"
            scan.completed_at = timezone.now()
            scan.result_summary = {
                "alerts_generated": alerts_created,
                "records_analyzed": len(features),
                "anomalies_found": len(anomalies),
                "rule_violations": len(rule_violations),
            }
            scan.save()

        if alerts_created > 0:
            send_notification.delay(
                notification_type="leakage_detected",
                organization_id=str(organization_id),
                context={
                    "scan_id": str(scan.id),
                    "alerts_count": alerts_created,
                    "total_estimated_leakage": str(
                        sum(s["estimated_amount"] for s in combined_scores if s["score"] >= detector.alert_threshold)
                    ),
                },
            )

        return {
            "status": "completed",
            "scan_id": str(scan.id),
            "alerts_created": alerts_created,
            "records_analyzed": len(features),
        }

    except Exception as exc:
        logger.exception(f"Error running leakage detection for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            if "scan" in locals():
                scan.status = "failed"
                scan.error_message = str(exc)
                scan.completed_at = timezone.now()
                scan.save()
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def detect_unbilled_hours(self, client_id):
    try:
        from apps.leakage.models import LeakageAlert
        from apps.leakage.services.unbilled import UnbilledHoursDetector
        from apps.contracts.models import Contract

        client_contracts = Contract.objects.filter(
            client_id=client_id,
            status="active",
        )

        if not client_contracts.exists():
            return {"status": "skipped", "reason": "no_active_contracts"}

        detector = UnbilledHoursDetector()
        unbilled_results = detector.detect(client_id)

        alerts_created = 0
        for result in unbilled_results:
            if result["unbilled_hours"] > detector.threshold:
                existing_alert = LeakageAlert.objects.filter(
                    client_id=client_id,
                    alert_type="unbilled_hours",
                    status="open",
                    evidence__contract_id=str(result["contract_id"]),
                ).exists()

                if not existing_alert:
                    LeakageAlert.objects.create(
                        organization_id=result["organization_id"],
                        client_id=client_id,
                        alert_type="unbilled_hours",
                        severity=detector.calculate_severity(result["unbilled_hours"]),
                        score=detector.calculate_score(result),
                        estimated_amount=result["estimated_amount"],
                        evidence={
                            "contract_id": str(result["contract_id"]),
                            "unbilled_hours": result["unbilled_hours"],
                            "period": result["period"],
                            "hourly_rate": str(result["hourly_rate"]),
                        },
                        status="open",
                        detected_at=timezone.now(),
                    )
                    alerts_created += 1

        return {
            "status": "completed",
            "client_id": str(client_id),
            "unbilled_entries": len(unbilled_results),
            "alerts_created": alerts_created,
        }

    except Exception as exc:
        logger.exception(f"Error detecting unbilled hours for client {client_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def detect_missed_escalations(self, organization_id):
    try:
        from apps.leakage.models import LeakageAlert
        from apps.leakage.services.escalation import EscalationDetector
        from apps.contracts.models import Contract

        detector = EscalationDetector()

        contracts_with_escalations = Contract.objects.filter(
            organization_id=organization_id,
            status="active",
            escalation_rate__isnull=False,
        )

        alerts_created = 0
        for contract in contracts_with_escalations:
            missed = detector.check_escalation(contract)

            if missed:
                existing = LeakageAlert.objects.filter(
                    organization_id=organization_id,
                    client_id=contract.client_id,
                    alert_type="missed_escalation",
                    status="open",
                    evidence__contract_id=str(contract.id),
                ).exists()

                if not existing:
                    LeakageAlert.objects.create(
                        organization_id=organization_id,
                        client_id=contract.client_id,
                        alert_type="missed_escalation",
                        severity="medium",
                        score=missed["score"],
                        estimated_amount=missed["estimated_amount"],
                        evidence={
                            "contract_id": str(contract.id),
                            "expected_rate": str(missed["expected_rate"]),
                            "current_rate": str(missed["current_rate"]),
                            "escalation_due_date": missed["due_date"],
                            "days_overdue": missed["days_overdue"],
                        },
                        status="open",
                        detected_at=timezone.now(),
                    )
                    alerts_created += 1

        return {
            "status": "completed",
            "contracts_checked": contracts_with_escalations.count(),
            "alerts_created": alerts_created,
        }

    except Exception as exc:
        logger.exception(f"Error detecting missed escalations for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def generate_leakage_report(self, organization_id):
    try:
        from apps.leakage.models import LeakageAlert, LeakageScan
        from apps.leakage.services.report import LeakageReportGenerator
        from apps.notifications.tasks import send_notification

        now = timezone.now()
        week_ago = now - timedelta(days=7)

        alerts = LeakageAlert.objects.filter(
            organization_id=organization_id,
            detected_at__gte=week_ago,
        )

        scans = LeakageScan.objects.filter(
            organization_id=organization_id,
            started_at__gte=week_ago,
        )

        report_generator = LeakageReportGenerator()
        report = report_generator.generate_weekly_report(
            organization_id=organization_id,
            alerts=alerts,
            scans=scans,
            period_start=week_ago,
            period_end=now,
        )

        send_notification.delay(
            notification_type="weekly_leakage_report",
            organization_id=str(organization_id),
            context={
                "report_id": str(report.id),
                "period": f"{week_ago.date().isoformat()} to {now.date().isoformat()}",
                "total_alerts": alerts.count(),
                "total_leakage_amount": str(
                    alerts.aggregate(total=models_Sum("estimated_amount"))["total"] or 0
                ),
                "resolved_count": alerts.filter(status="resolved").count(),
                "open_count": alerts.filter(status="open").count(),
            },
        )

        return {
            "status": "completed",
            "report_id": str(report.id),
            "alerts_included": alerts.count(),
        }

    except Exception as exc:
        logger.exception(f"Error generating leakage report for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}
