"""Invoice signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for Payment model."""
    if created:
        # Trigger revenue recognition event
        from apps.recognition.tasks import process_payment_recognition
        process_payment_recognition.delay(instance.id)
