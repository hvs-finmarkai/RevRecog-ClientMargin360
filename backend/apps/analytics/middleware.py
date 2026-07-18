import json
import threading
import re
from django.utils import timezone


FINANCIAL_ENDPOINTS = [
    "/api/v1/contracts/",
    "/api/v1/invoices/",
    "/api/v1/billing/",
    "/api/v1/recognition/",
    "/api/v1/collections/",
    "/api/v1/profitability/",
]

SENSITIVE_FIELDS = re.compile(
    r"(password|passwd|secret|token|api_key|access_key|private_key|credit_card|cvv|ssn)",
    re.IGNORECASE,
)

WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")


def _sanitize_body(body_bytes):
    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    if isinstance(data, dict):
        return {k: "***" if SENSITIVE_FIELDS.search(k) else v for k, v in data.items()}
    return data


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _is_financial_endpoint(path):
    return any(path.startswith(endpoint) for endpoint in FINANCIAL_ENDPOINTS)


def _save_audit_log(user, method, path, ip_address, user_agent, request_body, response_status, organization):
    from apps.analytics.models import AnalyticsEvent

    action_map = {
        "POST": "create",
        "PUT": "update",
        "PATCH": "partial_update",
        "DELETE": "delete",
    }

    event_data = {
        "method": method,
        "endpoint": path,
        "request_body": request_body,
        "response_status": response_status,
        "action": action_map.get(method, method.lower()),
    }

    AnalyticsEvent.objects.create(
        organization=organization,
        event_type=f"audit.{action_map.get(method, method.lower())}",
        event_category=AnalyticsEvent.EventCategory.USER_ACTION,
        entity_type=path.split("/")[3] if len(path.split("/")) > 3 else "",
        data=event_data,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        source="api",
    )


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in WRITE_METHODS:
            return self.get_response(request)

        if not _is_financial_endpoint(request.path):
            return self.get_response(request)

        request_body = _sanitize_body(request.body) if request.body else {}
        ip_address = _get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        response = self.get_response(request)

        user = request.user if hasattr(request, "user") and request.user.is_authenticated else None
        organization = user.organization if user and hasattr(user, "organization") else None

        if user and organization:
            thread = threading.Thread(
                target=_save_audit_log,
                args=(
                    user,
                    request.method,
                    request.path,
                    ip_address,
                    user_agent,
                    request_body,
                    response.status_code,
                    organization,
                ),
                daemon=True,
            )
            thread.start()

        return response
