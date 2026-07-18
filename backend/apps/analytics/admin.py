from django.contrib import admin
from .models import AnalyticsEvent, MetricSnapshot

admin.site.register(AnalyticsEvent)
admin.site.register(MetricSnapshot)
