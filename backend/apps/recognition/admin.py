from django.contrib import admin
from .models import RevenueSchedule, RevenueEntry, RecognitionRule, ASC606Compliance


@admin.register(RevenueSchedule)
class RevenueScheduleAdmin(admin.ModelAdmin):
    list_display = ['contract', 'start_date', 'end_date', 'total_amount']
    list_filter = ['start_date']
    search_fields = ['contract__name']


@admin.register(RevenueEntry)
class RevenueEntryAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'period', 'amount', 'status']
    list_filter = ['status']
    search_fields = ['schedule__contract__name']


@admin.register(RecognitionRule)
class RecognitionRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name']


@admin.register(ASC606Compliance)
class ASC606ComplianceAdmin(admin.ModelAdmin):
    list_display = ['contract', 'step', 'status', 'assessed_at']
    list_filter = ['step', 'status']
    search_fields = ['contract__name']
