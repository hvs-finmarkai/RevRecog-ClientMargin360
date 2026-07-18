"""Client admin configuration."""
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Client, ClientContact


class ClientContactInline(admin.TabularInline):
    model = ClientContact
    extra = 0


@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["name", "code", "tier", "status", "industry", "account_manager", "created_at"]
    list_filter = ["tier", "status", "industry"]
    search_fields = ["name", "code"]
    inlines = [ClientContactInline]


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ["name", "client", "email", "is_primary", "is_billing_contact"]
    list_filter = ["is_primary", "is_billing_contact"]
