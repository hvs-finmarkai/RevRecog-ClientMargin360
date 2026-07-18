"""Notifications signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification


@receiver(post_save, sender=Notification)
def notification_post_save(sender, instance, created, **kwargs):
    """Handle notification creation - push to WebSocket/email if needed."""
    if created and instance.channel in ["email", "both"]:
        pass  # Queue email sending
