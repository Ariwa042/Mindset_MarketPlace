from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'get_phone_number')
    
    def get_phone_number(self, obj):
        return obj.profile.phone_number
    get_phone_number.short_description = 'Phone Number'

admin.site.register(CustomUser, CustomUserAdmin)
