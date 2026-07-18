from django.contrib import admin
from .models import CostAllocation, OverheadAllocation, MarginCalculation, ProfitabilitySnapshot, BenchmarkData

admin.site.register(CostAllocation)
admin.site.register(OverheadAllocation)
admin.site.register(MarginCalculation)
admin.site.register(ProfitabilitySnapshot)
admin.site.register(BenchmarkData)
