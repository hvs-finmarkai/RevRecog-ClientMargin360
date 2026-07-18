"""Collections management admin configuration."""
from django.contrib import admin
from .models import CollectionEntry, CollectionAction, AgingReport


class CollectionActionInline(admin.TabularInline):
    model = CollectionAction
    extra = 0


@admin.register(CollectionEntry)
class CollectionEntryAdmin(admin.ModelAdmin):
    list_display = ["invoice", "client", "priority", "status", "days_overdue", "amount_outstanding"]
    list_filter = ["priority", "status"]
    inlines = [CollectionActionInline]


@admin.register(AgingReport)
class AgingReportAdmin(admin.ModelAdmin):
    list_display = ["client", "report_date", "current_amount", "days_1_30", "days_31_60", "days_61_90", "days_over_90"]
    list_filter = ["report_date"]
