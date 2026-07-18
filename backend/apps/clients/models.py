"""
Clients app models - Client, ClientContact, ClientAddress, ClientSegment.
Manages client master data, contacts, addresses, and segmentation.
"""

import uuid

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Validators
# =============================================================================

gstin_validator = RegexValidator(
    regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
    message="Enter a valid 15-character GSTIN.",
)

pan_validator = RegexValidator(
    regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
    message="Enter a valid 10-character PAN.",
)

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)


# =============================================================================
# Client Segment Model
# =============================================================================

class ClientSegment(BaseModel):
    """Client segmentation for classification and analysis."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    criteria = models.JSONField(
        default=dict,
        blank=True,
        help_text="Segmentation criteria as structured JSON",
    )
    min_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum revenue threshold for this segment",
    )
    max_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum revenue threshold (null = unlimited)",
    )
    color_code = models.CharField(
        max_length=7,
        blank=True,
        default="#3B82F6",
        help_text="Hex color for UI display",
    )

    class Meta:
        ordering = ["min_revenue"]
        verbose_name = "Client Segment"
        verbose_name_plural = "Client Segments"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["min_revenue", "max_revenue"]),
        ]

    def __str__(self):
        return self.name


# =============================================================================
# Client Model
# =============================================================================

class Client(BaseModel):
    """Client/Customer master data model."""

    class IndustryChoices(models.TextChoices):
        TECHNOLOGY = "technology", "Technology"
        BFSI = "bfsi", "Banking, Financial Services & Insurance"
        HEALTHCARE = "healthcare", "Healthcare"
        RETAIL = "retail", "Retail & E-Commerce"
        MANUFACTURING = "manufacturing", "Manufacturing"
        TELECOM = "telecom", "Telecommunications"
        MEDIA = "media", "Media & Entertainment"
        ENERGY = "energy", "Energy & Utilities"
        EDUCATION = "education", "Education"
        GOVERNMENT = "government", "Government"
        AUTOMOTIVE = "automotive", "Automotive"
        PHARMA = "pharma", "Pharmaceuticals"
        REAL_ESTATE = "real_estate", "Real Estate"
        LOGISTICS = "logistics", "Logistics & Transportation"
        OTHER = "other", "Other"

    class StatusChoices(models.TextChoices):
        PROSPECT = "prospect", "Prospect"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        CHURNED = "churned", "Churned"
        SUSPENDED = "suspended", "Suspended"

    class PaymentTermChoices(models.TextChoices):
        NET_15 = "net_15", "Net 15"
        NET_30 = "net_30", "Net 30"
        NET_45 = "net_45", "Net 45"
        NET_60 = "net_60", "Net 60"
        NET_90 = "net_90", "Net 90"
        IMMEDIATE = "immediate", "Immediate"
        ADVANCE = "advance", "Advance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="clients",
    )
    name = models.CharField(max_length=255, db_index=True)
    legal_name = models.CharField(max_length=255, blank=True, default="")
    industry = models.CharField(
        max_length=20,
        choices=IndustryChoices.choices,
        default=IndustryChoices.TECHNOLOGY,
    )
    segment = models.ForeignKey(
        ClientSegment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients",
    )
    gstin = models.CharField(
        max_length=15,
        blank=True,
        default="",
        validators=[gstin_validator],
        help_text="Goods and Services Tax Identification Number",
    )
    pan = models.CharField(
        max_length=10,
        blank=True,
        default="",
        validators=[pan_validator],
        help_text="Permanent Account Number",
    )
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10, blank=True, default="")
    contact_person = models.CharField(max_length=200, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(
        max_length=17,
        blank=True,
        default="",
        validators=[phone_validator],
    )
    website = models.URLField(max_length=500, blank=True, default="")
    payment_terms = models.CharField(
        max_length=20,
        choices=PaymentTermChoices.choices,
        default=PaymentTermChoices.NET_30,
    )
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Risk score (0-100, higher = more risky)",
    )
    health_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Health score (0-100, higher = healthier)",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        db_index=True,
    )
    logo_url = models.URLField(max_length=500, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["name"]),
            models.Index(fields=["industry"]),
            models.Index(fields=["gstin"]),
            models.Index(fields=["risk_score"]),
            models.Index(fields=["health_score"]),
        ]

    def __str__(self):
        return self.name


# =============================================================================
# Client Contact Model
# =============================================================================

class ClientContact(BaseModel):
    """Contact persons associated with a client."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, blank=True, default="")
    email = models.EmailField()
    phone = models.CharField(
        max_length=17,
        blank=True,
        default="",
        validators=[phone_validator],
    )
    is_primary = models.BooleanField(default=False)
    is_billing_contact = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-is_primary", "name"]
        verbose_name = "Client Contact"
        verbose_name_plural = "Client Contacts"
        indexes = [
            models.Index(fields=["client", "is_primary"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.client.name})"


# =============================================================================
# Client Address Model
# =============================================================================

class ClientAddress(BaseModel):
    """Multiple addresses for a client (billing, shipping, registered, etc.)."""

    class AddressType(models.TextChoices):
        REGISTERED = "registered", "Registered Office"
        BILLING = "billing", "Billing Address"
        SHIPPING = "shipping", "Shipping Address"
        BRANCH = "branch", "Branch Office"
        WAREHOUSE = "warehouse", "Warehouse"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.REGISTERED,
    )
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="India")
    gstin = models.CharField(
        max_length=15,
        blank=True,
        default="",
        validators=[gstin_validator],
        help_text="State-specific GSTIN for this address",
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "address_type"]
        verbose_name = "Client Address"
        verbose_name_plural = "Client Addresses"
        indexes = [
            models.Index(fields=["client", "address_type"]),
            models.Index(fields=["state"]),
        ]

    def __str__(self):
        return f"{self.client.name} - {self.get_address_type_display()} ({self.city})"

    @property
    def full_address(self):
        parts = [self.line1]
        if self.line2:
            parts.append(self.line2)
        parts.extend([self.city, self.state, self.pincode, self.country])
        return ", ".join(parts)
