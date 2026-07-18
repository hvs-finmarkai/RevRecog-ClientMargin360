"""
Profitability app models - CostAllocation, OverheadAllocation,
MarginCalculation, ProfitabilitySnapshot, BenchmarkData.
Manages cost allocation, margin analysis, and profitability tracking.
"""

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Cost Allocation Model
# =============================================================================

class CostAllocation(BaseModel):
    """Cost allocation to clients and contracts for profitability analysis."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="cost_allocations",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="cost_allocations",
        null=True,
        blank=True,
    )
    period_start = models.DateField()
    period_end = models.DateField()
    direct_labor_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    direct_material_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    subcontractor_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    travel_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    technology_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    allocated_overhead = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    headcount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="FTE headcount allocated",
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-period_start"]
        verbose_name = "Cost Allocation"
        verbose_name_plural = "Cost Allocations"
        unique_together = ["client", "contract", "period_start", "period_end"]
        indexes = [
            models.Index(fields=["client", "period_start"]),
            models.Index(fields=["contract", "period_start"]),
            models.Index(fields=["period_start", "period_end"]),
        ]

    def __str__(self):
        return f"{self.client.name} - {self.period_start} to {self.period_end} ({self.total_cost})"

    @property
    def direct_costs(self):
        return (
            self.direct_labor_cost
            + self.direct_material_cost
            + self.subcontractor_cost
            + self.travel_cost
            + self.technology_cost
        )

    def save(self, *args, **kwargs):
        self.total_cost = self.direct_costs + self.allocated_overhead
        super().save(*args, **kwargs)


# =============================================================================
# Overhead Allocation Model
# =============================================================================

class OverheadAllocation(BaseModel):
    """Overhead cost allocation across clients/contracts."""

    class AllocationMethod(models.TextChoices):
        REVENUE_BASED = "revenue_based", "Revenue-Based"
        HEADCOUNT = "headcount", "Headcount-Based"
        EQUAL = "equal", "Equal Distribution"
        HOURS_BASED = "hours_based", "Hours-Based"
        CUSTOM = "custom", "Custom Formula"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="overhead_allocations",
        null=True,
        blank=True,
    )
    period_start = models.DateField()
    period_end = models.DateField()
    total_overhead = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    allocation_method = models.CharField(
        max_length=20,
        choices=AllocationMethod.choices,
        default=AllocationMethod.REVENUE_BASED,
    )
    allocations = models.JSONField(
        default=dict,
        help_text="Breakdown of allocations per client/contract as JSON",
    )
    status = models.CharField(
        max_length=20,
        default="draft",
        choices=[
            ("draft", "Draft"),
            ("applied", "Applied"),
            ("revised", "Revised"),
        ],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-period_start"]
        verbose_name = "Overhead Allocation"
        verbose_name_plural = "Overhead Allocations"
        indexes = [
            models.Index(fields=["period_start", "period_end"]),
            models.Index(fields=["allocation_method"]),
        ]

    def __str__(self):
        return f"Overhead {self.period_start} to {self.period_end} ({self.total_overhead})"


# =============================================================================
# Margin Calculation Model
# =============================================================================

class MarginCalculation(BaseModel):
    """Margin calculations for clients and contracts."""

    class StatusChoices(models.TextChoices):
        HEALTHY = "healthy", "Healthy"
        WATCH = "watch", "Watch"
        AT_RISK = "at_risk", "At Risk"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="margin_calculations",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="margin_calculations",
        null=True,
        blank=True,
    )
    period_start = models.DateField()
    period_end = models.DateField()
    revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    direct_costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    allocated_overhead = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    gross_margin = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Revenue - Direct Costs",
    )
    gross_margin_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="Gross margin percentage",
    )
    net_margin = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Revenue - Direct Costs - Overhead",
    )
    net_margin_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="Net margin percentage",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.HEALTHY,
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-period_start"]
        verbose_name = "Margin Calculation"
        verbose_name_plural = "Margin Calculations"
        unique_together = ["client", "contract", "period_start", "period_end"]
        indexes = [
            models.Index(fields=["client", "period_start"]),
            models.Index(fields=["contract", "period_start"]),
            models.Index(fields=["status"]),
            models.Index(fields=["gross_margin_pct"]),
            models.Index(fields=["net_margin_pct"]),
        ]

    def __str__(self):
        return f"{self.client.name} - {self.period_start} (Margin: {self.net_margin_pct}%)"

    def save(self, *args, **kwargs):
        self.gross_margin = self.revenue - self.direct_costs
        self.net_margin = self.revenue - self.direct_costs - self.allocated_overhead
        if self.revenue > 0:
            self.gross_margin_pct = (self.gross_margin / self.revenue) * 100
            self.net_margin_pct = (self.net_margin / self.revenue) * 100
        else:
            self.gross_margin_pct = 0
            self.net_margin_pct = 0
        # Auto-determine status
        if self.net_margin_pct >= 25:
            self.status = self.StatusChoices.HEALTHY
        elif self.net_margin_pct >= 15:
            self.status = self.StatusChoices.WATCH
        elif self.net_margin_pct >= 5:
            self.status = self.StatusChoices.AT_RISK
        else:
            self.status = self.StatusChoices.CRITICAL
        super().save(*args, **kwargs)


# =============================================================================
# Profitability Snapshot Model
# =============================================================================

class ProfitabilitySnapshot(BaseModel):
    """Periodic profitability snapshots for clients (trailing 12 months)."""

    class TrendDirection(models.TextChoices):
        IMPROVING = "improving", "Improving"
        STABLE = "stable", "Stable"
        DECLINING = "declining", "Declining"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="profitability_snapshots",
    )
    snapshot_date = models.DateField(db_index=True)
    trailing_12m_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    trailing_12m_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    trailing_12m_margin_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
    )
    trend_direction = models.CharField(
        max_length=10,
        choices=TrendDirection.choices,
        default=TrendDirection.STABLE,
    )
    rank = models.PositiveIntegerField(
        default=0,
        help_text="Client rank by profitability within the organization",
    )
    active_contracts = models.PositiveIntegerField(default=0)
    total_headcount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    revenue_per_head = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        ordering = ["-snapshot_date", "rank"]
        verbose_name = "Profitability Snapshot"
        verbose_name_plural = "Profitability Snapshots"
        unique_together = ["client", "snapshot_date"]
        indexes = [
            models.Index(fields=["client", "snapshot_date"]),
            models.Index(fields=["snapshot_date", "rank"]),
            models.Index(fields=["trend_direction"]),
            models.Index(fields=["trailing_12m_margin_pct"]),
        ]

    def __str__(self):
        return f"{self.client.name} - {self.snapshot_date} (Margin: {self.trailing_12m_margin_pct}%)"


# =============================================================================
# Benchmark Data Model
# =============================================================================

class BenchmarkData(BaseModel):
    """Industry/billing model benchmarks for margin comparison."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="benchmarks",
        null=True,
        blank=True,
    )
    period = models.DateField(help_text="Period this benchmark applies to")
    billing_model = models.CharField(
        max_length=50,
        help_text="Billing model code this benchmark is for",
    )
    industry = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Industry segment for this benchmark",
    )
    avg_margin = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Average margin percentage",
    )
    median_margin = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Median margin percentage",
    )
    top_quartile = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Top quartile (75th percentile) margin",
    )
    bottom_quartile = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Bottom quartile (25th percentile) margin",
    )
    client_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of clients in this benchmark sample",
    )
    data_source = models.CharField(
        max_length=200,
        blank=True,
        default="internal",
        help_text="Source of benchmark data",
    )

    class Meta:
        ordering = ["-period"]
        verbose_name = "Benchmark Data"
        verbose_name_plural = "Benchmark Data"
        unique_together = ["period", "billing_model", "industry"]
        indexes = [
            models.Index(fields=["period", "billing_model"]),
            models.Index(fields=["industry"]),
        ]

    def __str__(self):
        return f"Benchmark {self.billing_model} - {self.period} (Avg: {self.avg_margin}%)"
