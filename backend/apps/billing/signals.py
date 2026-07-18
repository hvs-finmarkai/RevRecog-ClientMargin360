"""Billing signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BillingMilestone


@receiver(post_save, sender=BillingMilestone)
def milestone_post_save(sender, instance, **kwargs):
    """Trigger invoice generation when a milestone is achieved."""
    if instance.status == BillingMilestone.Status.ACHIEVED:
        from apps.invoices.tasks import generate_milestone_invoice
        generate_milestone_invoice.delay(instance.id)
