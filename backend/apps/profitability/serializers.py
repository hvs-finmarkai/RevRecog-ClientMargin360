"""
Profitability app serializers - CostAllocationSerializer, MarginCalculationSerializer,
ProfitabilitySnapshotSerializer, BenchmarkDataSerializer, OverheadAllocationSerializer.
"""

from rest_framework import serializers

from .models import (
    BenchmarkData,
    CostAllocation,
    MarginCalculation,
    OverheadAllocation,
    ProfitabilitySnapshot,
)


# =============================================================================
# Cost Allocation Serializer
# =============================================================================

class CostAllocationSerializer(serializers.ModelSerializer):
    """Serializer for CostAllocation model."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True, default=None
    )
    direct_costs = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = CostAllocation
        fields = [
            "id", "client", "client_name",
            "contract", "contract_number",
            "period_start", "period_end",
            "direct_labor_cost", "direct_material_cost",
            "subcontractor_cost", "travel_cost", "technology_cost",
            "allocated_overhead", "total_cost",
            "headcount", "direct_costs", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "total_cost", "created_at", "updated_at"]

    def validate(self, attrs):
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")

        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError(
                {"period_end": "Period end must be after period start."}
            )

        # Validate no negative costs
        cost_fields = [
            "direct_labor_cost", "direct_material_cost",
            "subcontractor_cost", "travel_cost", "technology_cost",
            "allocated_overhead",
        ]
        for field in cost_fields:
            value = attrs.get(field, 0)
            if value and value < 0:
                raise serializers.ValidationError(
                    {field: "Cost values cannot be negative."}
                )

        return attrs


# =============================================================================
# Overhead Allocation Serializer
# =============================================================================

class OverheadAllocationSerializer(serializers.ModelSerializer):
    """Serializer for OverheadAllocation model."""

    allocation_method_display = serializers.CharField(
        source="get_allocation_method_display", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )

    class Meta:
        model = OverheadAllocation
        fields = [
            "id", "organization", "organization_name",
            "period_start", "period_end",
            "total_overhead", "allocation_method",
            "allocation_method_display",
            "allocations", "status", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")

        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError(
                {"period_end": "Period end must be after period start."}
            )

        total_overhead = attrs.get("total_overhead", 0)
        if total_overhead <= 0:
            raise serializers.ValidationError(
                {"total_overhead": "Total overhead must be greater than zero."}
            )

        return attrs


# =============================================================================
# Margin Calculation Serializer
# =============================================================================

class MarginCalculationSerializer(serializers.ModelSerializer):
    """Serializer for MarginCalculation model."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True, default=None
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    margin_health = serializers.SerializerMethodField()

    class Meta:
        model = MarginCalculation
        fields = [
            "id", "client", "client_name",
            "contract", "contract_number",
            "period_start", "period_end",
            "revenue", "direct_costs", "allocated_overhead",
            "gross_margin", "gross_margin_pct",
            "net_margin", "net_margin_pct",
            "status", "status_display", "notes",
            "margin_health",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "gross_margin", "gross_margin_pct",
            "net_margin", "net_margin_pct", "status",
            "created_at", "updated_at",
        ]

    def get_margin_health(self, obj):
        """Return color-coded margin health indicator."""
        pct = obj.net_margin_pct
        if pct >= 25:
            return {"color": "green", "label": "Healthy", "icon": "up"}
        elif pct >= 15:
            return {"color": "yellow", "label": "Watch", "icon": "stable"}
        elif pct >= 5:
            return {"color": "orange", "label": "At Risk", "icon": "down"}
        else:
            return {"color": "red", "label": "Critical", "icon": "down"}

    def validate(self, attrs):
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")

        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError(
                {"period_end": "Period end must be after period start."}
            )

        revenue = attrs.get("revenue", 0)
        if revenue < 0:
            raise serializers.ValidationError(
                {"revenue": "Revenue cannot be negative."}
            )

        return attrs


# =============================================================================
# Profitability Snapshot Serializer
# =============================================================================

class ProfitabilitySnapshotSerializer(serializers.ModelSerializer):
    """Serializer for ProfitabilitySnapshot model."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    trend_direction_display = serializers.CharField(
        source="get_trend_direction_display", read_only=True
    )
    margin_status = serializers.SerializerMethodField()

    class Meta:
        model = ProfitabilitySnapshot
        fields = [
            "id", "client", "client_name", "snapshot_date",
            "trailing_12m_revenue", "trailing_12m_cost",
            "trailing_12m_margin_pct",
            "trend_direction", "trend_direction_display",
            "rank", "active_contracts", "total_headcount",
            "revenue_per_head", "margin_status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_margin_status(self, obj):
        pct = obj.trailing_12m_margin_pct
        if pct >= 25:
            return "healthy"
        elif pct >= 15:
            return "watch"
        elif pct >= 5:
            return "at_risk"
        return "critical"


# =============================================================================
# Benchmark Data Serializer
# =============================================================================

class BenchmarkDataSerializer(serializers.ModelSerializer):
    """Serializer for BenchmarkData model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )
    spread = serializers.SerializerMethodField()

    class Meta:
        model = BenchmarkData
        fields = [
            "id", "organization", "organization_name",
            "period", "billing_model", "industry",
            "avg_margin", "median_margin",
            "top_quartile", "bottom_quartile",
            "client_count", "data_source", "spread",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_spread(self, obj):
        """Calculate the spread between top and bottom quartile."""
        return obj.top_quartile - obj.bottom_quartile

    def validate(self, attrs):
        top_quartile = attrs.get("top_quartile", 0)
        bottom_quartile = attrs.get("bottom_quartile", 0)
        avg_margin = attrs.get("avg_margin", 0)
        median_margin = attrs.get("median_margin", 0)

        if top_quartile < bottom_quartile:
            raise serializers.ValidationError(
                {"top_quartile": "Top quartile must be >= bottom quartile."}
            )

        if avg_margin < bottom_quartile or avg_margin > top_quartile:
            raise serializers.ValidationError(
                {"avg_margin": "Average margin should be between bottom and top quartiles."}
            )

        if median_margin < bottom_quartile or median_margin > top_quartile:
            raise serializers.ValidationError(
                {"median_margin": "Median margin should be between bottom and top quartiles."}
            )

        return attrs
