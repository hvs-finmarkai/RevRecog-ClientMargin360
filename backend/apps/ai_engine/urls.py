"""AI Engine app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AIRecommendationViewSet, ContractParsingViewSet

router = DefaultRouter()
router.register(r"recommendations", AIRecommendationViewSet, basename="ai-recommendation")
router.register(r"contract-parsing", ContractParsingViewSet, basename="contract-parsing")

app_name = "ai_engine"

urlpatterns = [
    path("", include(router.urls)),
]
