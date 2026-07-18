import logging
from datetime import timedelta

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=30,
    acks_late=True,
)
def send_notification(self, notification_type=None, organization_id=None, context=None, notification_id=None):
    try:
        from apps.notifications.models import Notification, NotificationPreference
        from apps.notifications.services.dispatcher import NotificationDispatcher

        dispatcher = NotificationDispatcher()

        if notification_id:
            notification = Notification.objects.get(id=notification_id)
        else:
            recipients = dispatcher.resolve_recipients(
                notification_type=notification_type,
                organization_id=organization_id,
            )

            notifications = []
            for recipient in recipients:
                preference = NotificationPreference.objects.filter(
                    user=recipient,
                    notification_type=notification_type,
                ).first()

                if preference and not preference.is_enabled:
                    continue

                notification = Notification.objects.create(
                    user=recipient,
                    organization_id=organization_id,
                    notification_type=notification_type,
                    title=dispatcher.render_title(notification_type, context),
                    message=dispatcher.render_message(notification_type, context),
                    context=context or {},
                    channels=dispatcher.get_channels(preference),
                    status="pending",
                )
                notifications.append(notification)

            for notification in notifications:
                _deliver_notification(notification, dispatcher)

            return {
                "status": "completed",
                "notifications_sent": len(notifications),
                "notification_type": notification_type,
            }

        _deliver_notification(notification, dispatcher)
        return {
            "status": "completed",
            "notification_id": str(notification.id),
        }

    except Notification.DoesNotExist:
        logger.error(f"Notification not found: {notification_id}")
        return {"status": "failed", "reason": "notification_not_found"}
    except Exception as exc:
        logger.exception(f"Error sending notification: {notification_type or notification_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


def _deliver_notification(notification, dispatcher):
    from apps.notifications.models import Notification

    try:
        for channel in notification.channels:
            if channel == "in_app":
                notification.status = "delivered"
                notification.delivered_at = timezone.now()
            elif channel == "email":
                dispatcher.send_email(notification)
            elif channel == "slack":
                dispatcher.send_slack(notification)
            elif channel == "webhook":
                dispatcher.send_webhook(notification)

        notification.status = "delivered"
        notification.delivered_at = timezone.now()
        notification.save(update_fields=["status", "delivered_at"])
    except Exception as exc:
        notification.status = "failed"
        notification.error_message = str(exc)
        notification.save(update_fields=["status", "error_message"])
        raise


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=30,
    acks_late=True,
)
def send_email_notification(self, user_id, template_id, context):
    try:
        from apps.notifications.models import EmailLog
        from apps.notifications.services.email import EmailService
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(id=user_id)

        email_service = EmailService()
        rendered = email_service.render_template(template_id, context)

        email_log = EmailLog.objects.create(
            user=user,
            template_id=template_id,
            subject=rendered["subject"],
            recipient_email=user.email,
            status="sending",
        )

        email_service.send(
            to_email=user.email,
            subject=rendered["subject"],
            html_body=rendered["html_body"],
            text_body=rendered["text_body"],
        )

        email_log.status = "sent"
        email_log.sent_at = timezone.now()
        email_log.save(update_fields=["status", "sent_at"])

        return {
            "status": "sent",
            "email_log_id": str(email_log.id),
            "recipient": user.email,
        }

    except User.DoesNotExist:
        logger.error(f"User not found: {user_id}")
        return {"status": "failed", "reason": "user_not_found"}
    except Exception as exc:
        logger.exception(f"Error sending email to user {user_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            if "email_log" in locals():
                email_log.status = "failed"
                email_log.error_message = str(exc)
                email_log.save(update_fields=["status", "error_message"])
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def process_alert_rules(self, organization_id):
    try:
        from apps.notifications.models import AlertRule, AlertRuleExecution
        from apps.notifications.services.rule_engine import AlertRuleEngine

        rule_engine = AlertRuleEngine()

        active_rules = AlertRule.objects.filter(
            organization_id=organization_id,
            is_active=True,
        )

        rules_triggered = 0
        rules_checked = 0

        for rule in active_rules:
            rules_checked += 1

            execution = AlertRuleExecution.objects.create(
                rule=rule,
                organization_id=organization_id,
                started_at=timezone.now(),
                status="running",
            )

            try:
                result = rule_engine.evaluate(rule)

                execution.completed_at = timezone.now()
                execution.result = result

                if result["triggered"]:
                    rules_triggered += 1
                    execution.status = "triggered"

                    send_notification.delay(
                        notification_type=f"alert_rule_{rule.alert_type}",
                        organization_id=str(organization_id),
                        context={
                            "rule_id": str(rule.id),
                            "rule_name": rule.name,
                            "triggered_value": result["current_value"],
                            "threshold": result["threshold"],
                            "severity": rule.severity,
                            "details": result.get("details", {}),
                        },
                    )

                    rule.last_triggered_at = timezone.now()
                    rule.trigger_count = (rule.trigger_count or 0) + 1
                    rule.save(update_fields=["last_triggered_at", "trigger_count"])
                else:
                    execution.status = "not_triggered"

                execution.save(update_fields=["completed_at", "result", "status"])

            except Exception as rule_exc:
                execution.status = "error"
                execution.error_message = str(rule_exc)
                execution.completed_at = timezone.now()
                execution.save(update_fields=["status", "error_message", "completed_at"])
                logger.warning(f"Rule {rule.id} evaluation failed: {rule_exc}")

        return {
            "status": "completed",
            "rules_checked": rules_checked,
            "rules_triggered": rules_triggered,
        }

    except Exception as exc:
        logger.exception(f"Error processing alert rules for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def cleanup_old_notifications(self):
    try:
        from apps.notifications.models import Notification, EmailLog, AlertRuleExecution

        now = timezone.now()

        read_cutoff = now - timedelta(days=90)
        deleted_read = Notification.objects.filter(
            is_read=True,
            delivered_at__lt=read_cutoff,
        ).delete()[0]

        unread_cutoff = now - timedelta(days=180)
        deleted_unread = Notification.objects.filter(
            is_read=False,
            created_at__lt=unread_cutoff,
        ).delete()[0]

        failed_cutoff = now - timedelta(days=30)
        deleted_failed = Notification.objects.filter(
            status="failed",
            created_at__lt=failed_cutoff,
        ).delete()[0]

        email_log_cutoff = now - timedelta(days=365)
        deleted_email_logs = EmailLog.objects.filter(
            created_at__lt=email_log_cutoff,
        ).delete()[0]

        execution_cutoff = now - timedelta(days=90)
        deleted_executions = AlertRuleExecution.objects.filter(
            started_at__lt=execution_cutoff,
        ).delete()[0]

        return {
            "status": "completed",
            "deleted_read_notifications": deleted_read,
            "deleted_unread_notifications": deleted_unread,
            "deleted_failed_notifications": deleted_failed,
            "deleted_email_logs": deleted_email_logs,
            "deleted_rule_executions": deleted_executions,
            "total_deleted": deleted_read + deleted_unread + deleted_failed + deleted_email_logs + deleted_executions,
        }

    except Exception as exc:
        logger.exception("Error cleaning up old notifications")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}
