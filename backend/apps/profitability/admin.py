from django.contrib import admin

from .models import CostAllocation, OverheadAllocation, MarginCalculation, ProfitabilitySnapshot, BenchmarkData


@admin.register(CostAllocation)
class CostAllocationAdmin(admin.ModelAdmin):
    list_display = ["client", "contract", "period_start", "period_end", "total_cost"]
    list_filter = ["period_start"]
    search_fields = ["client__name"]


@admin.register(OverheadAllocation)
class OverheadAllocationAdmin(admin.ModelAdmin):
    list_display = ["organization", "period_start", "period_end", "total_overhead", "allocation_method"]
    list_filter = ["allocation_method", "status"]


@admin.register(MarginCalculation)
class MarginCalculationAdmin(admin.ModelAdmin):
    list_display = ["client", "revenue", "direct_costs", "net_margin_pct", "status"]
    list_filter = ["status", "period_start"]
    search_fields = ["client__name"]


@admin.register(ProfitabilitySnapshot)
class ProfitabilitySnapshotAdmin(admin.ModelAdmin):
    list_display = ["client", "snapshot_date", "trailing_12m_revenue", "trailing_12m_margin_pct", "trend_direction"]
    list_filter = ["trend_direction", "snapshot_date"]
    search_fields = ["client__name"]


@admin.register(BenchmarkData)
class BenchmarkDataAdmin(admin.ModelAdmin):
    list_display = ["period", "billing_model", "industry", "avg_margin", "client_count"]
    list_filter = ["billing_model", "industry"]
