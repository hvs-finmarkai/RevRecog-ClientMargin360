"""Reports signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Report


@receiver(post_save, sender=Report)
def report_post_save(sender, instance, **kwargs):
    """Notify user when report generation is complete."""
    if instance.status == "ready" and instance.generated_by:
        from apps.notifications.tasks import send_report_ready_notification
        send_report_ready_notification.delay(instance.id, instance.generated_by_id)
