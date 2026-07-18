from django.urls import path
from .views import AuthViewSet

login_view = AuthViewSet.as_view({"post": "login"})
logout_view = AuthViewSet.as_view({"post": "logout"})
refresh_view = AuthViewSet.as_view({"post": "refresh"})
register_view = AuthViewSet.as_view({"post": "register"})


def setup_view(request):
    from django.http import JsonResponse
    from .models import User
    if not User.objects.filter(email="admin@finmark.ai").exists():
        User.objects.create_superuser(
            email="admin@finmark.ai",
            password="Finmark@2026",
            first_name="Admin",
            last_name="Finmark",
        )
        return JsonResponse({"status": "created", "email": "admin@finmark.ai"})
    return JsonResponse({"status": "exists", "email": "admin@finmark.ai"})


urlpatterns = [
    path("login", login_view, name="auth-login"),
    path("login/", login_view, name="auth-login-slash"),
    path("logout", logout_view, name="auth-logout"),
    path("logout/", logout_view, name="auth-logout-slash"),
    path("refresh", refresh_view, name="auth-refresh"),
    path("refresh/", refresh_view, name="auth-refresh-slash"),
    path("register", register_view, name="auth-register"),
    path("register/", register_view, name="auth-register-slash"),
    path("setup/", setup_view, name="auth-setup"),
]
