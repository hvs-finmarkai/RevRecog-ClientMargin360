from django.contrib import admin
from .models import NotificationTemplate, Notification, NotificationPreference, AlertRule

admin.site.register(NotificationTemplate)
admin.site.register(Notification)
admin.site.register(NotificationPreference)
admin.site.register(AlertRule)
