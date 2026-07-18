from django.contrib import admin
from .models import LeakageDetection, LeakageRule, LeakageAlert, LeakageResolution

admin.site.register(LeakageDetection)
admin.site.register(LeakageRule)
admin.site.register(LeakageAlert)
admin.site.register(LeakageResolution)
