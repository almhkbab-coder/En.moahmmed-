from django.contrib import admin
from .models import Clinic, ClinicBranch, WorkingHours, ClinicHoliday


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 0


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'created_at')


@admin.register(ClinicBranch)
class ClinicBranchAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'city_ar', 'phone', 'whatsapp', 'is_primary', 'is_active')
    list_filter = ('is_primary', 'is_active', 'city_ar')
    inlines = [WorkingHoursInline]


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('branch', 'day_of_week', 'morning_start', 'morning_end', 'evening_start', 'evening_end', 'slot_duration_minutes', 'is_closed')
    list_filter = ('branch', 'day_of_week', 'is_closed')


@admin.register(ClinicHoliday)
class ClinicHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason_ar', 'branch')
    list_filter = ('branch', 'date')

