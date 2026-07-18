"""Contract signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Contract


@receiver(post_save, sender=Contract)
def contract_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for Contract model."""
    if created and instance.document:
        from .tasks import parse_contract_document
        parse_contract_document.delay(instance.id)
