import functools
import json
import threading
from django.utils import timezone


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _compute_changes(old_instance, new_instance):
    if old_instance is None or new_instance is None:
        return {}
    changes = {}
    for field in old_instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(new_instance, field_name, None)
        if old_value != new_value:
            changes[field_name] = {
                "old": str(old_value) if old_value is not None else None,
                "new": str(new_value) if new_value is not None else None,
            }
    return changes


def _save_event(user, organization, action_type, entity_type, entity_id, ip_address, user_agent, changes):
    from apps.analytics.models import AnalyticsEvent

    AnalyticsEvent.objects.create(
        organization=organization,
        event_type=action_type,
        event_category=AnalyticsEvent.EventCategory.BUSINESS_EVENT,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else "",
        data={
            "changes": changes,
            "timestamp": timezone.now().isoformat(),
        },
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        source="api",
    )


def audit_action(action_type):
    def decorator(view_method):
        @functools.wraps(view_method)
        def wrapped(self, request, *args, **kwargs):
            old_instance = None
            if request.method in ("PUT", "PATCH") and hasattr(self, "get_object"):
                try:
                    obj = self.get_object()
                    old_instance = type(obj).objects.get(pk=obj.pk)
                except Exception:
                    old_instance = None

            response = view_method(self, request, *args, **kwargs)

            user = request.user if hasattr(request, "user") and request.user.is_authenticated else None
            if not user:
                return response

            organization = user.organization if hasattr(user, "organization") else None
            if not organization:
                return response

            entity_type = ""
            entity_id = ""

            if hasattr(self, "get_object"):
                try:
                    obj = self.get_object()
                    entity_type = type(obj).__name__
                    entity_id = str(obj.pk)
                except Exception:
                    pass

            if not entity_type and hasattr(response, "data") and isinstance(response.data, dict):
                entity_id = response.data.get("id", "")

            if not entity_type:
                parts = action_type.split(".")
                if parts:
                    entity_type = parts[0]

            changes = {}
            if old_instance and request.method in ("PUT", "PATCH"):
                try:
                    new_instance = type(old_instance).objects.get(pk=old_instance.pk)
                    changes = _compute_changes(old_instance, new_instance)
                except Exception:
                    pass

            ip_address = _get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            thread = threading.Thread(
                target=_save_event,
                args=(user, organization, action_type, entity_type, entity_id, ip_address, user_agent, changes),
                daemon=True,
            )
            thread.start()

            return response

        return wrapped

    return decorator
