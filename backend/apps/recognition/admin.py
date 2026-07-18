from django.contrib import admin

from .models import RevenueSchedule, RevenueEntry, RecognitionRule, ASC606Compliance


@admin.register(RevenueSchedule)
class RevenueScheduleAdmin(admin.ModelAdmin):
    list_display = ["contract", "total_amount", "recognized_amount", "deferred_amount", "pattern", "status"]
    list_filter = ["pattern", "status"]
    search_fields = ["contract__contract_number"]


@admin.register(RevenueEntry)
class RevenueEntryAdmin(admin.ModelAdmin):
    list_display = ["schedule", "period_start", "period_end", "amount", "entry_type", "status"]
    list_filter = ["entry_type", "status"]


@admin.register(RecognitionRule)
class RecognitionRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "billing_model", "recognition_pattern", "timing", "is_active"]
    list_filter = ["billing_model", "recognition_pattern", "is_active"]
    search_fields = ["name"]


@admin.register(ASC606Compliance)
class ASC606ComplianceAdmin(admin.ModelAdmin):
    list_display = ["contract", "compliance_status", "last_review_date"]
    list_filter = ["compliance_status"]
    search_fields = ["contract__contract_number"]
