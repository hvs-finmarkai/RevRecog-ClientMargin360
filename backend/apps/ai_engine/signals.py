"""AI Engine signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AIProcessingJob


@receiver(post_save, sender=AIProcessingJob)
def ai_job_post_save(sender, instance, **kwargs):
    """Notify stakeholders when an AI job completes."""
    if instance.status == "completed" and instance.triggered_by:
        pass  # Send notification about job completion
