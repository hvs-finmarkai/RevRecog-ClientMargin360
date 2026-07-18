"""Users app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, OrganizationViewSet, RoleViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"auth", AuthViewSet, basename="auth")

app_name = "users"

urlpatterns = [
    path("", include(router.urls)),
]
