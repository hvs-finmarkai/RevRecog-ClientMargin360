"""Collections management signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CollectionEntry


@receiver(post_save, sender=CollectionEntry)
def collection_entry_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for CollectionEntry model."""
    if created and instance.priority in ["high", "critical"]:
        from apps.notifications.tasks import send_collection_alert
        send_collection_alert.delay(instance.id)
