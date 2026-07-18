"""Profitability admin configuration."""
from django.contrib import admin
from .models import ClientProfitability, ProjectProfitability, CostEntry


@admin.register(ClientProfitability)
class ClientProfitabilityAdmin(admin.ModelAdmin):
    list_display = ["client", "period", "revenue", "gross_margin_pct", "health_score", "trend"]
    list_filter = ["period", "trend"]
    search_fields = ["client__name"]


@admin.register(ProjectProfitability)
class ProjectProfitabilityAdmin(admin.ModelAdmin):
    list_display = ["contract", "period", "revenue", "margin_pct", "is_at_risk"]
    list_filter = ["period", "is_at_risk"]


@admin.register(CostEntry)
class CostEntryAdmin(admin.ModelAdmin):
    list_display = ["contract", "client", "cost_type", "amount", "date", "is_billable"]
    list_filter = ["cost_type", "is_billable", "period"]
