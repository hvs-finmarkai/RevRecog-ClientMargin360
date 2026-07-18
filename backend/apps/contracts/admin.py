from django.contrib import admin
from .models import Contract, ContractVersion, ContractTerm, PerformanceObligation, ContractDocument, ContractAmendment

admin.site.register(Contract)
admin.site.register(ContractVersion)
admin.site.register(ContractTerm)
admin.site.register(PerformanceObligation)
admin.site.register(ContractDocument)
admin.site.register(ContractAmendment)
