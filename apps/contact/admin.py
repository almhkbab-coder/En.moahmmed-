from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'subject', 'is_read', 'replied', 'created_at')
    list_filter = ('is_read', 'replied', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'ip_address')

