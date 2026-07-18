"""
Celery configuration for RevRecog AI + ClientMargin360.
"""
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("revrecog")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# Periodic task schedule
app.conf.beat_schedule = {
    "process-pending-recognitions": {
        "task": "apps.recognition.tasks.process_pending_recognitions",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "recognition"},
    },
    "detect-revenue-leakage": {
        "task": "apps.leakage.tasks.run_leakage_detection",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "analytics"},
    },
    "update-profitability-metrics": {
        "task": "apps.profitability.tasks.recalculate_all_margins",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "analytics"},
    },
    "generate-aging-reports": {
        "task": "apps.collections_mgmt.tasks.generate_aging_reports",
        "schedule": crontab(hour=6, minute=0, day_of_week="mon"),
        "options": {"queue": "reports"},
    },
    "sync-external-data": {
        "task": "apps.integrations.tasks.sync_all_integrations",
        "schedule": crontab(hour="*/4", minute=30),
        "options": {"queue": "integrations"},
    },
    "send-collection-reminders": {
        "task": "apps.collections_mgmt.tasks.send_collection_reminders",
        "schedule": crontab(hour=9, minute=0, day_of_week="mon-fri"),
        "options": {"queue": "notifications"},
    },
}

app.conf.task_routes = {
    "apps.recognition.tasks.*": {"queue": "recognition"},
    "apps.leakage.tasks.*": {"queue": "analytics"},
    "apps.profitability.tasks.*": {"queue": "analytics"},
    "apps.reports.tasks.*": {"queue": "reports"},
    "apps.ai_engine.tasks.*": {"queue": "ai"},
    "apps.integrations.tasks.*": {"queue": "integrations"},
    "apps.notifications.tasks.*": {"queue": "notifications"},
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery connectivity."""
    print(f"Request: {self.request!r}")
