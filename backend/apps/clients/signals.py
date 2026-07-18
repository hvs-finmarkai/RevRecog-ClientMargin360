"""Client signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Client


@receiver(post_save, sender=Client)
def client_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for Client model."""
    if created:
        pass  # Initialize client analytics, send notifications, etc.
