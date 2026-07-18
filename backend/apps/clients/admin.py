from django.contrib import admin
from .models import ClientSegment, Client, ClientContact, ClientAddress


@admin.register(ClientSegment)
class ClientSegmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'segment', 'is_active', 'created_at']
    list_filter = ['is_active', 'segment']
    search_fields = ['name']


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ['client', 'name', 'email', 'phone']
    list_filter = ['client']
    search_fields = ['name', 'email']


@admin.register(ClientAddress)
class ClientAddressAdmin(admin.ModelAdmin):
    list_display = ['client', 'city', 'country']
    list_filter = ['country']
    search_fields = ['client__name', 'city']
