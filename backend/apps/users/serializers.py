"""
Users app serializers - UserSerializer, UserCreateSerializer, OrganizationSerializer,
RoleSerializer, UserActivitySerializer, LoginSerializer, TokenSerializer,
PasswordChangeSerializer.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Organization, Role, User, UserActivity


# =============================================================================
# Organization Serializer
# =============================================================================

class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""

    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id", "name", "domain", "subscription_plan", "is_active",
            "settings", "logo", "address", "phone", "tax_id",
            "timezone", "currency", "user_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_user_count(self, obj):
        return obj.users.filter(is_active=True, is_deleted=False).count()

    def validate_domain(self, value):
        qs = Organization.objects.filter(domain=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("An organization with this domain already exists.")
        return value


# =============================================================================
# Role Serializer
# =============================================================================

class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""

    permission_count = serializers.SerializerMethodField()
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )

    class Meta:
        model = Role
        fields = [
            "id", "name", "description", "organization", "organization_name",
            "is_system_role", "permission_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_system_role", "created_at", "updated_at"]

    def get_permission_count(self, obj):
        return obj.permissions.count()

    def validate_name(self, value):
        qs = Role.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value


# =============================================================================
# User Serializer (Read)
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Read serializer for User model with nested related objects."""

    full_name = serializers.SerializerMethodField()
    organization_detail = OrganizationSerializer(source="organization", read_only=True)
    role_detail = RoleSerializer(source="role", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "phone", "organization", "organization_detail",
            "role", "role_detail", "is_active", "is_staff",
            "avatar", "mfa_enabled", "date_joined",
            "last_login", "last_login_ip",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "email", "date_joined", "last_login",
            "last_login_ip", "created_at", "updated_at",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


# =============================================================================
# User Create Serializer (Write)
# =============================================================================

class UserCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating users with password validation."""

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "organization", "role", "password", "password_confirm",
            "avatar", "is_active",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        validate_password(password)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# =============================================================================
# User Activity Serializer
# =============================================================================

class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = UserActivity
        fields = [
            "id", "user", "user_email", "user_name",
            "activity_type", "description", "entity_type",
            "entity_id", "ip_address", "user_agent",
            "metadata", "created_at",
        ]
        read_only_fields = [
            "id", "user", "ip_address", "user_agent", "created_at",
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name()


# =============================================================================
# Login Serializer
# =============================================================================

class LoginSerializer(serializers.Serializer):
    """Serializer for user authentication."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email", "").lower()
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                "Both email and password are required."
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid email or password. Please try again."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account has been deactivated. Please contact support."
            )

        attrs["user"] = user
        return attrs


# =============================================================================
# Token Serializer
# =============================================================================

class TokenSerializer(serializers.Serializer):
    """Serializer for token responses."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)


# =============================================================================
# Password Change Serializer
# =============================================================================

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )

        if attrs.get("old_password") == new_password:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from the current password."}
            )

        validate_password(new_password, self.context["request"].user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        return user
