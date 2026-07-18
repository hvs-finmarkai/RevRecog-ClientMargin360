"""
Users app models - Custom User, Organization, Role, UserActivity.
Provides authentication, authorization, and audit trail functionality.
"""

import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Permission,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


# =============================================================================
# Validators
# =============================================================================

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)

domain_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$',
    message="Enter a valid domain name.",
)


# =============================================================================
# Base Model
# =============================================================================

class BaseModel(models.Model):
    """Abstract base model with common fields for all models."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

    def restore(self):
        self.is_deleted = False
        self.save(update_fields=["is_deleted", "updated_at"])


# =============================================================================
# Organization Model
# =============================================================================

class Organization(BaseModel):
    """Organization/Tenant model for multi-tenancy support."""

    class SubscriptionPlan(models.TextChoices):
        FREE = "free", "Free"
        STARTER = "starter", "Starter"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    domain = models.CharField(
        max_length=255,
        unique=True,
        validators=[domain_validator],
        help_text="Organization's primary domain (e.g., company.com)",
    )
    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
    )
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Organization-specific settings and preferences",
    )
    logo = models.URLField(max_length=500, blank=True, default="")
    address = models.TextField(blank=True, default="")
    phone = models.CharField(
        max_length=17,
        blank=True,
        default="",
        validators=[phone_validator],
    )
    tax_id = models.CharField(max_length=50, blank=True, default="")
    timezone = models.CharField(max_length=50, default="Asia/Kolkata")
    currency = models.CharField(max_length=3, default="INR")

    class Meta:
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        indexes = [
            models.Index(fields=["name", "is_active"]),
            models.Index(fields=["subscription_plan"]),
        ]

    def __str__(self):
        return self.name


# =============================================================================
# Role Model
# =============================================================================

class Role(BaseModel):
    """Role model with permission-based access control."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="roles",
        null=True,
        blank=True,
        help_text="Null means system-wide role",
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_roles",
    )
    is_system_role = models.BooleanField(
        default=False,
        help_text="System roles cannot be deleted or modified",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        indexes = [
            models.Index(fields=["name", "organization"]),
        ]

    def __str__(self):
        return self.name


# =============================================================================
# Custom User Manager
# =============================================================================

class UserManager(BaseUserManager):
    """Custom manager for User model with email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def active(self):
        return self.filter(is_active=True, is_deleted=False)


# =============================================================================
# Custom User Model
# =============================================================================

class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model using email as the authentication field."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(
        max_length=17,
        blank=True,
        default="",
        validators=[phone_validator],
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    avatar = models.URLField(max_length=500, blank=True, default="")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True, default="")
    date_joined = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def full_name(self):
        return self.get_full_name()


# =============================================================================
# User Activity Model
# =============================================================================

class UserActivity(models.Model):
    """Audit trail for user actions within the system."""

    class ActivityType(models.TextChoices):
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PASSWORD_CHANGE = "password_change", "Password Change"
        PROFILE_UPDATE = "profile_update", "Profile Update"
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        EXPORT = "export", "Export"
        IMPORT = "import", "Import"
        VIEW = "view", "View"
        APPROVE = "approve", "Approve"
        REJECT = "reject", "Reject"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        db_index=True,
    )
    description = models.TextField(blank=True, default="")
    entity_type = models.CharField(max_length=100, blank=True, default="")
    entity_id = models.CharField(max_length=255, blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        indexes = [
            models.Index(fields=["user", "activity_type"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} at {self.created_at}"
