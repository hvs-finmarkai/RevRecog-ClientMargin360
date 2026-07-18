"""Billing admin configuration."""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import BillingSchedule, BillingMilestone, BillingRate


class BillingMilestoneInline(admin.TabularInline):
    model = BillingMilestone
    extra = 0


@admin.register(BillingSchedule)
class BillingScheduleAdmin(admin.ModelAdmin):
    list_display = ["contract", "frequency", "amount", "start_date", "end_date", "is_active"]
    list_filter = ["frequency", "is_active"]
    inlines = [BillingMilestoneInline]


@admin.register(BillingMilestone)
class BillingMilestoneAdmin(SimpleHistoryAdmin):
    list_display = ["name", "schedule", "amount", "status", "target_date", "achieved_date"]
    list_filter = ["status"]


@admin.register(BillingRate)
class BillingRateAdmin(admin.ModelAdmin):
    list_display = ["contract", "role_name", "hourly_rate", "daily_rate", "is_active"]
    list_filter = ["is_active"]
