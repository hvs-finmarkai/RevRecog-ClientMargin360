from django.contrib import admin
from .models import Receivable, PaymentReceipt, CollectionSchedule, AgingBucket, DunningRule, CashForecast


@admin.register(Receivable)
class ReceivableAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount_due', 'amount_paid', 'status', 'due_date']
    list_filter = ['status', 'due_date']
    search_fields = ['invoice__invoice_number']


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['receivable', 'amount', 'payment_method', 'received_at']
    list_filter = ['payment_method']
    search_fields = ['receivable__invoice__invoice_number']


@admin.register(CollectionSchedule)
class CollectionScheduleAdmin(admin.ModelAdmin):
    list_display = ['receivable', 'scheduled_date', 'action_type', 'status']
    list_filter = ['action_type', 'status']
    search_fields = ['receivable__invoice__invoice_number']


@admin.register(AgingBucket)
class AgingBucketAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_days', 'max_days']
    search_fields = ['name']


@admin.register(DunningRule)
class DunningRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'days_overdue', 'action_type', 'is_active']
    list_filter = ['action_type', 'is_active']
    search_fields = ['name']


@admin.register(CashForecast)
class CashForecastAdmin(admin.ModelAdmin):
    list_display = ['period', 'expected_collections', 'actual_collections', 'created_at']
    list_filter = ['period']
    search_fields = ['period']
