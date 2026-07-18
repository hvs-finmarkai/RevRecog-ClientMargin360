"""User background tasks."""
from celery import shared_task
from django.utils import timezone


@shared_task
def deactivate_inactive_users(days=90):
    """Deactivate users who haven't logged in for the specified number of days."""
    from .models import User

    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    inactive_users = User.objects.filter(
        last_login__lt=cutoff_date,
        is_active=True,
        is_superuser=False,
    )
    count = inactive_users.update(is_active=False)
    return f"Deactivated {count} inactive users"
