"""Leakage signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LeakageAlert


@receiver(post_save, sender=LeakageAlert)
def leakage_alert_post_save(sender, instance, created, **kwargs):
    """Notify stakeholders when a critical leakage alert is created."""
    if created and instance.severity in ["high", "critical"]:
        from apps.notifications.tasks import send_leakage_notification
        send_leakage_notification.delay(instance.id)
