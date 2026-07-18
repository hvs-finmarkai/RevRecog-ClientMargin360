from django.contrib import admin
from .models import ClientSegment, Client, ClientContact, ClientAddress

admin.site.register(ClientSegment)
admin.site.register(Client)
admin.site.register(ClientContact)
admin.site.register(ClientAddress)
