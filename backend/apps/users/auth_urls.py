from django.urls import path
from .views import AuthViewSet

login_view = AuthViewSet.as_view({"post": "login"})
logout_view = AuthViewSet.as_view({"post": "logout"})
refresh_view = AuthViewSet.as_view({"post": "refresh"})
register_view = AuthViewSet.as_view({"post": "register"})

urlpatterns = [
    path("login", login_view, name="auth-login"),
    path("login/", login_view, name="auth-login-slash"),
    path("logout", logout_view, name="auth-logout"),
    path("logout/", logout_view, name="auth-logout-slash"),
    path("refresh", refresh_view, name="auth-refresh"),
    path("refresh/", refresh_view, name="auth-refresh-slash"),
    path("register", register_view, name="auth-register"),
    path("register/", register_view, name="auth-register-slash"),
]
