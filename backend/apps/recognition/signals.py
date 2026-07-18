"""Revenue recognition signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RevenueRecognitionEvent


@receiver(post_save, sender=RevenueRecognitionEvent)
def recognition_event_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for recognition events."""
    if instance.status == "recognized":
        # Update deferred revenue balances
        from .tasks import update_deferred_balance
        update_deferred_balance.delay(instance.id)
