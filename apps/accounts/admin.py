from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية والصلاحيات', {'fields': ('role', 'phone_number', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('معلومات إضافية والصلاحيات', {'fields': ('email', 'role', 'phone_number', 'profile_image')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

