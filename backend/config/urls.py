"""
Root URL configuration for RevRecog AI + ClientMargin360.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/contracts/", include("apps.contracts.urls")),
    path("api/v1/clients/", include("apps.clients.urls")),
    path("api/v1/billing/", include("apps.billing.urls")),
    path("api/v1/invoices/", include("apps.invoices.urls")),
    path("api/v1/recognition/", include("apps.recognition.urls")),
    path("api/v1/leakage/", include("apps.leakage.urls")),
    path("api/v1/profitability/", include("apps.profitability.urls")),
    path("api/v1/collections/", include("apps.collections_mgmt.urls")),
    path("api/v1/ai/", include("apps.ai_engine.urls")),
    path("api/v1/integrations/", include("apps.integrations.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Debug toolbar and media files in development
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
