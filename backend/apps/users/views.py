"""
Users app views - UserViewSet, OrganizationViewSet, RoleViewSet, AuthViewSet.
Provides user management, organization CRUD, role management, and authentication endpoints.
"""

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Organization, Role, UserActivity
from .serializers import (
    LoginSerializer,
    OrganizationSerializer,
    PasswordChangeSerializer,
    RoleSerializer,
    TokenSerializer,
    UserActivitySerializer,
    UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users within an organization.
    Supports CRUD operations with organization-scoped filtering.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active", "role", "organization"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering_fields = ["date_joined", "email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.filter(is_deleted=False)
        return User.objects.filter(
            organization=user.organization,
            is_deleted=False,
        )

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "activities":
            return UserActivitySerializer
        return UserSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def activities(self, request, pk=None):
        """Get activity log for a specific user."""
        user = self.get_object()
        activities = UserActivity.objects.filter(user=user).order_by("-created_at")[:50]
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a user account."""
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        return Response({"detail": "User deactivated successfully."})

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a user account."""
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active", "updated_at"])
        return Response({"detail": "User activated successfully."})


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    Admin-only access for full CRUD, authenticated users can view their own org.
    """

    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["subscription_plan", "is_active"]
    search_fields = ["name", "domain"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.filter(is_deleted=False)
        return Organization.objects.filter(
            id=user.organization_id,
            is_deleted=False,
        )

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def users(self, request, pk=None):
        """List all users in an organization."""
        org = self.get_object()
        users = User.objects.filter(organization=org, is_deleted=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Get organization statistics."""
        org = self.get_object()
        return Response({
            "total_users": org.users.filter(is_deleted=False).count(),
            "active_users": org.users.filter(is_active=True, is_deleted=False).count(),
            "total_roles": org.roles.filter(is_deleted=False).count(),
        })


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles within an organization.
    """

    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_system_role", "organization"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Role.objects.filter(is_deleted=False)
        return Role.objects.filter(
            organization=user.organization,
            is_deleted=False,
        ) | Role.objects.filter(
            organization__isnull=True,
            is_deleted=False,
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.is_system_role:
            return Response(
                {"detail": "System roles cannot be deleted."},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.soft_delete()


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication actions: login, logout, refresh, register, change-password.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def get_serializer_class(self):
        if self.action == "login":
            return LoginSerializer
        if self.action == "register":
            return UserCreateSerializer
        if self.action == "change_password":
            return PasswordChangeSerializer
        if self.action == "refresh":
            return TokenSerializer
        return LoginSerializer

    def get_permissions(self):
        if self.action in ["login", "register", "refresh"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["post"])
    def login(self, request):
        """Authenticate user and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Account is deactivated."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        user.last_login = timezone.now()
        user.last_login_ip = request.META.get("REMOTE_ADDR")
        user.save(update_fields=["last_login", "last_login_ip"])

        UserActivity.objects.create(
            user=user,
            activity_type=UserActivity.ActivityType.LOGIN,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })

    @action(detail=False, methods=["post"])
    def logout(self, request):
        """Blacklist the refresh token to log out."""
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            if request.user.is_authenticated:
                UserActivity.objects.create(
                    user=request.user,
                    activity_type=UserActivity.ActivityType.LOGOUT,
                    ip_address=request.META.get("REMOTE_ADDR"),
                )

            return Response({"detail": "Successfully logged out."})
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        """Refresh access token using refresh token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["post"])
    def register(self, request):
        """Register a new user account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        """Change the authenticated user's password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])

        UserActivity.objects.create(
            user=user,
            activity_type=UserActivity.ActivityType.PASSWORD_CHANGE,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return Response({"detail": "Password changed successfully."})
