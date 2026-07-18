from django.contrib import admin
from .models import Organization, Role, User, UserActivity

admin.site.register(Organization)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(UserActivity)
