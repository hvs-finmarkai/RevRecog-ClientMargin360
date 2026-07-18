from django.contrib import admin
from .models import ReportTemplate, ReportSchedule, ReportExport, Dashboard, DashboardWidget

admin.site.register(ReportTemplate)
admin.site.register(ReportSchedule)
admin.site.register(ReportExport)
admin.site.register(Dashboard)
admin.site.register(DashboardWidget)
