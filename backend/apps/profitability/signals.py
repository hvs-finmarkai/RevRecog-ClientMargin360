"""Profitability signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CostEntry


@receiver(post_save, sender=CostEntry)
def cost_entry_post_save(sender, instance, created, **kwargs):
    """Recalculate project profitability when a cost entry is added."""
    if created:
        from .tasks import calculate_project_profitability
        calculate_project_profitability.delay(instance.contract_id, instance.period)
