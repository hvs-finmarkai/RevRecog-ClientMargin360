from django.contrib import admin
from .models import InvoiceTemplate, Invoice, InvoiceLineItem, CreditNote, DebitNote, InvoiceApproval

admin.site.register(InvoiceTemplate)
admin.site.register(Invoice)
admin.site.register(InvoiceLineItem)
admin.site.register(CreditNote)
admin.site.register(DebitNote)
admin.site.register(InvoiceApproval)
