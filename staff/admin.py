from django.contrib import admin
from .models import StaffMember, ActivityLog, SiteAnalytics

@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'is_active', 'last_login']
    list_filter = ['role', 'is_active', 'department']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['staff', 'action', 'content_type', 'timestamp', 'ip_address']
    list_filter = ['action', 'content_type', 'timestamp']
    search_fields = ['staff__user__email', 'description']

@admin.register(SiteAnalytics)
class SiteAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'page_views', 'unique_visitors', 'total_orders', 'total_sales']
    list_filter = ['date']
