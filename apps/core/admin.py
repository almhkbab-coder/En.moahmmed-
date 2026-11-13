from django.contrib import admin
from .models import SiteSettings, ActivityLog


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('clinic_name_ar', 'doctor_name_ar', 'phone', 'whatsapp')

    def has_add_permission(self, request):
        # Disallow adding more than one settings instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'target_model', 'target_id', 'ip_address')
    list_filter = ('action', 'target_model', 'created_at')
    search_fields = ('action', 'details', 'target_model', 'target_id')
    readonly_fields = ('user', 'action', 'target_model', 'target_id', 'details', 'ip_address', 'created_at')

