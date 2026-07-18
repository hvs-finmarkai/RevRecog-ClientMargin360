"""Integrations signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Integration


@receiver(post_save, sender=Integration)
def integration_post_save(sender, instance, created, **kwargs):
    """Trigger initial sync when integration is activated."""
    if not created and instance.status == "active":
        pass  # Could trigger initial data pull
