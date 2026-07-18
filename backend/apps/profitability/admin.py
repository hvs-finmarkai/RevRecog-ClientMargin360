from django.contrib import admin
from .models import CostAllocation, OverheadAllocation, MarginCalculation, ProfitabilitySnapshot, BenchmarkData


@admin.register(CostAllocation)
class CostAllocationAdmin(admin.ModelAdmin):
    list_display = ['contract', 'cost_type', 'amount', 'period']
    list_filter = ['cost_type']
    search_fields = ['contract__name']


@admin.register(OverheadAllocation)
class OverheadAllocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'allocation_method', 'amount', 'period']
    list_filter = ['allocation_method']
    search_fields = ['name']


@admin.register(MarginCalculation)
class MarginCalculationAdmin(admin.ModelAdmin):
    list_display = ['contract', 'revenue', 'cost', 'margin_percentage', 'calculated_at']
    list_filter = ['calculated_at']
    search_fields = ['contract__name']


@admin.register(ProfitabilitySnapshot)
class ProfitabilitySnapshotAdmin(admin.ModelAdmin):
    list_display = ['period', 'total_revenue', 'total_cost', 'net_margin']
    list_filter = ['period']
    search_fields = ['period']


@admin.register(BenchmarkData)
class BenchmarkDataAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'metric_type', 'value']
    list_filter = ['industry', 'metric_type']
    search_fields = ['name']
