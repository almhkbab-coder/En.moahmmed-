from django.contrib import admin
from .models import Patient, Appointment, AppointmentStatusHistory


class AppointmentStatusHistoryInline(admin.TabularInline):
    model = AppointmentStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'notes', 'timestamp')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'email', 'created_at')
    search_fields = ('phone_number', 'email', 'name_search_token')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'patient', 'branch', 'appointment_date', 'appointment_time', 'duration_minutes', 'end_time', 'service', 'status', 'created_at')
    list_filter = ('status', 'branch', 'appointment_date')
    search_fields = ('patient__phone_number', 'patient__name_search_token', 'booking_id', 'visit_reason')
    inlines = [AppointmentStatusHistoryInline]

