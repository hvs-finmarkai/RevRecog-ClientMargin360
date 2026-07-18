from django.contrib import admin
from .models import RevenueSchedule, RevenueEntry, RecognitionRule, ASC606Compliance

admin.site.register(RevenueSchedule)
admin.site.register(RevenueEntry)
admin.site.register(RecognitionRule)
admin.site.register(ASC606Compliance)
