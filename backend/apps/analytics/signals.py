"""Analytics signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MetricSnapshot


@receiver(post_save, sender=MetricSnapshot)
def metric_snapshot_post_save(sender, instance, created, **kwargs):
    """Handle metric snapshot creation."""
    pass  # Could trigger cache invalidation or WebSocket push
