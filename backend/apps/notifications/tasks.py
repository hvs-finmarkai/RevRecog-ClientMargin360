"""Notification background tasks."""
from celery import shared_task


@shared_task
def send_leakage_notification(alert_id):
    """Send notification about a leakage alert."""
    from apps.leakage.models import LeakageAlert
    from .models import Notification

    alert = LeakageAlert.objects.select_related("contract__owner").get(id=alert_id)
    if alert.contract.owner:
        Notification.objects.create(
            recipient=alert.contract.owner,
            notification_type="warning",
            title=f"Revenue Leakage Detected: {alert.title}",
            message=f"Estimated leakage: ${alert.estimated_leakage_amount}. Severity: {alert.severity}",
            action_url=f"/leakage/alerts/{alert.id}",
            metadata={"alert_id": alert.id, "severity": alert.severity},
        )
    return f"Sent leakage notification for alert {alert.id}"


@shared_task
def send_collection_alert(collection_entry_id):
    """Send notification about a high-priority collection entry."""
    from apps.collections_mgmt.models import CollectionEntry
    from .models import Notification

    entry = CollectionEntry.objects.select_related("client").get(id=collection_entry_id)
    if entry.assigned_to:
        Notification.objects.create(
            recipient=entry.assigned_to,
            notification_type="warning",
            title=f"High Priority Collection: {entry.client.name}",
            message=f"Outstanding: ${entry.amount_outstanding}. {entry.days_overdue} days overdue.",
            action_url=f"/collections/entries/{entry.id}",
            metadata={"entry_id": entry.id, "priority": entry.priority},
        )
    return f"Sent collection alert for entry {collection_entry_id}"


@shared_task
def send_report_ready_notification(report_id, user_id):
    """Notify user that a report is ready for download."""
    from apps.users.models import User
    from .models import Notification

    user = User.objects.get(id=user_id)
    Notification.objects.create(
        recipient=user,
        notification_type="success",
        title="Report Ready",
        message="Your requested report has been generated and is ready for download.",
        action_url=f"/reports/{report_id}/download",
        metadata={"report_id": report_id},
    )
    return f"Sent report ready notification to user {user_id}"
