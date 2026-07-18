from django.contrib import admin
from .models import IntegrationConfig, SyncLog, WebhookConfig, APIKey

admin.site.register(IntegrationConfig)
admin.site.register(SyncLog)
admin.site.register(WebhookConfig)
admin.site.register(APIKey)
