"""Integrations background tasks."""
import time
from celery import shared_task
from django.utils import timezone


@shared_task
def sync_all_integrations():
    """Sync data from all active integrations."""
    from .models import Integration
    integrations = Integration.objects.filter(status="active")
    for integration in integrations:
        sync_integration.delay(integration.id)
    return f"Queued sync for {integrations.count()} integrations"


@shared_task
def sync_integration(integration_id):
    """Sync data from a specific integration."""
    from .models import Integration, SyncLog

    integration = Integration.objects.get(id=integration_id)
    start_time = timezone.now()

    sync_log = SyncLog.objects.create(
        integration=integration,
        status=SyncLog.SyncStatus.SUCCESS,
        started_at=start_time,
    )

    try:
        # Integration-specific sync logic
        records_synced = 0
        time.sleep(0.1)  # Simulated processing

        sync_log.records_synced = records_synced
        sync_log.completed_at = timezone.now()
        sync_log.duration_seconds = (timezone.now() - start_time).total_seconds()
        sync_log.save()

        integration.last_sync_at = timezone.now()
        integration.last_error = ""
        integration.save()

        return f"Synced {records_synced} records from {integration.name}"
    except Exception as e:
        sync_log.status = SyncLog.SyncStatus.FAILED
        sync_log.error_details = [str(e)]
        sync_log.completed_at = timezone.now()
        sync_log.save()

        integration.status = Integration.Status.ERROR
        integration.last_error = str(e)
        integration.save()
        raise
