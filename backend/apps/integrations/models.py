"""
Integrations app models - IntegrationConfig, SyncLog, WebhookConfig, APIKey.
Manages third-party integrations, sync operations, webhooks, and API keys.
"""

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Integration Config Model
# =============================================================================

class IntegrationConfig(BaseModel):
    """Configuration for third-party integrations."""

    class ProviderChoices(models.TextChoices):
        TALLY = "tally", "Tally"
        SAP = "sap", "SAP"
        SALESFORCE = "salesforce", "Salesforce"
        ZOHO = "zoho", "Zoho"
        JIRA = "jira", "Jira"
        FRESHDESK = "freshdesk", "Freshdesk"
        EXCEL = "excel", "Excel Import/Export"
        QUICKBOOKS = "quickbooks", "QuickBooks"
        XERO = "xero", "Xero"
        HUBSPOT = "hubspot", "HubSpot"
        SLACK = "slack", "Slack"
        TEAMS = "teams", "Microsoft Teams"
        GOOGLE_SHEETS = "google_sheets", "Google Sheets"

    class SyncFrequency(models.TextChoices):
        REALTIME = "realtime", "Real-time"
        HOURLY = "hourly", "Hourly"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MANUAL = "manual", "Manual"

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        ERROR = "error", "Error"
        CONFIGURING = "configuring", "Configuring"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="integrations",
    )
    provider = models.CharField(
        max_length=20,
        choices=ProviderChoices.choices,
        db_index=True,
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Custom name for this integration instance",
    )
    config = models.JSONField(
        default=dict,
        help_text="Integration configuration (encrypted sensitive fields)",
    )
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.CharField(
        max_length=10,
        choices=SyncFrequency.choices,
        default=SyncFrequency.DAILY,
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.CONFIGURING,
    )
    error_message = models.TextField(blank=True, default="")
    last_error_at = models.DateTimeField(null=True, blank=True)
    sync_mappings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Field mappings between systems",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["provider", "name"]
        verbose_name = "Integration Config"
        verbose_name_plural = "Integration Configs"
        unique_together = ["organization", "provider", "name"]
        indexes = [
            models.Index(fields=["organization", "provider"]),
            models.Index(fields=["provider", "is_active"]),
            models.Index(fields=["status"]),
            models.Index(fields=["last_sync"]),
        ]

    def __str__(self):
        display_name = self.name or self.get_provider_display()
        return f"{display_name} ({self.organization.name})"


# =============================================================================
# Sync Log Model
# =============================================================================

class SyncLog(BaseModel):
    """Log of synchronization operations."""

    class SyncType(models.TextChoices):
        FULL = "full", "Full Sync"
        INCREMENTAL = "incremental", "Incremental Sync"
        DELTA = "delta", "Delta Sync"
        MANUAL = "manual", "Manual Trigger"

    class StatusChoices(models.TextChoices):
        STARTED = "started", "Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PARTIAL = "partial", "Partial Success"
        CANCELLED = "cancelled", "Cancelled"

    class DirectionChoices(models.TextChoices):
        INBOUND = "inbound", "Inbound (Pull)"
        OUTBOUND = "outbound", "Outbound (Push)"
        BIDIRECTIONAL = "bidirectional", "Bidirectional"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(
        IntegrationConfig,
        on_delete=models.CASCADE,
        related_name="sync_logs",
    )
    sync_type = models.CharField(
        max_length=15,
        choices=SyncType.choices,
        default=SyncType.INCREMENTAL,
    )
    direction = models.CharField(
        max_length=15,
        choices=DirectionChoices.choices,
        default=DirectionChoices.INBOUND,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_synced = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    records_skipped = models.PositiveIntegerField(default=0)
    errors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of error details",
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.STARTED,
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_syncs",
    )
    summary = models.JSONField(
        default=dict,
        blank=True,
        help_text="Summary of what was synced",
    )

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Sync Log"
        verbose_name_plural = "Sync Logs"
        indexes = [
            models.Index(fields=["integration", "status"]),
            models.Index(fields=["started_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["sync_type"]),
        ]

    def __str__(self):
        return f"{self.integration} - {self.get_sync_type_display()} ({self.get_status_display()})"

    @property
    def duration_seconds(self):
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def success_rate(self):
        total = self.records_synced + self.records_failed
        if total > 0:
            return (self.records_synced / total) * 100
        return 0


# =============================================================================
# Webhook Config Model
# =============================================================================

class WebhookConfig(BaseModel):
    """Webhook configurations for event notifications."""

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        FAILED = "failed", "Failed (Too Many Errors)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="webhooks",
    )
    name = models.CharField(max_length=200, blank=True, default="")
    url = models.URLField(max_length=500)
    events = models.JSONField(
        default=list,
        help_text="List of event types to trigger this webhook",
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Webhook signing secret for verification",
    )
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    last_response_code = models.PositiveIntegerField(null=True, blank=True)
    failure_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    timeout_seconds = models.PositiveIntegerField(default=30)
    headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom headers to include in webhook requests",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Webhook Config"
        verbose_name_plural = "Webhook Configs"
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name or self.url} ({self.organization.name})"


# =============================================================================
# API Key Model
# =============================================================================

class APIKey(BaseModel):
    """API keys for external access to the system."""

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(
        max_length=200,
        help_text="Descriptive name for the API key",
    )
    key_prefix = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="First few characters of key for identification",
    )
    key_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="Hashed API key value",
    )
    permissions = models.JSONField(
        default=list,
        help_text="List of permission scopes granted to this key",
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Key expiration date (null = never expires)",
    )
    last_used = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    rate_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Requests per hour limit",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_api_keys",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["key_hash"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() >= self.expires_at
        return False
