from django.contrib import admin
from .models import Receivable, PaymentReceipt, CollectionSchedule, AgingBucket, DunningRule, CashForecast

admin.site.register(Receivable)
admin.site.register(PaymentReceipt)
admin.site.register(CollectionSchedule)
admin.site.register(AgingBucket)
admin.site.register(DunningRule)
admin.site.register(CashForecast)
