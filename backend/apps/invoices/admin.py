from django.contrib import admin
from .models import InvoiceTemplate, Invoice, InvoiceLineItem, CreditNote, DebitNote, InvoiceApproval


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'status', 'total_amount', 'due_date']
    list_filter = ['status', 'due_date']
    search_fields = ['invoice_number', 'client__name']


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'amount']
    search_fields = ['description']


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['invoice__invoice_number', 'reason']


@admin.register(DebitNote)
class DebitNoteAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['invoice__invoice_number', 'reason']


@admin.register(InvoiceApproval)
class InvoiceApprovalAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'approver', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['invoice__invoice_number']
