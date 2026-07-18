from django.contrib import admin
from .models import BillingModel, RateCard, RateCardItem, BillingPeriod, BillingSchedule, EscalationRule


@admin.register(BillingModel)
class BillingModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'created_at']
    list_filter = ['model_type']
    search_fields = ['name']


@admin.register(RateCard)
class RateCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'effective_date']
    list_filter = ['effective_date']
    search_fields = ['name', 'client__name']


@admin.register(RateCardItem)
class RateCardItemAdmin(admin.ModelAdmin):
    list_display = ['rate_card', 'description', 'rate']
    search_fields = ['description']


@admin.register(BillingPeriod)
class BillingPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    list_filter = ['start_date']
    search_fields = ['name']


@admin.register(BillingSchedule)
class BillingScheduleAdmin(admin.ModelAdmin):
    list_display = ['contract', 'frequency', 'next_billing_date']
    list_filter = ['frequency']
    search_fields = ['contract__name']


@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'percentage', 'frequency']
    search_fields = ['name']
