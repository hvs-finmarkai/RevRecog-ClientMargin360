from django.contrib import admin
from .models import Organization, Role, User, UserActivity


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'organization', 'is_active']
    list_filter = ['is_active', 'organization']
    search_fields = ['email', 'first_name', 'last_name']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at']
    list_filter = ['activity_type']
    search_fields = ['user__email']
