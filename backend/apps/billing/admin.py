from django.contrib import admin
from .models import BillingModel, RateCard, RateCardItem, BillingPeriod, BillingSchedule, EscalationRule

admin.site.register(BillingModel)
admin.site.register(RateCard)
admin.site.register(RateCardItem)
admin.site.register(BillingPeriod)
admin.site.register(BillingSchedule)
admin.site.register(EscalationRule)
