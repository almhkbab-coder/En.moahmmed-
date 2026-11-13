from django.contrib import admin
from .models import DoctorProfile, Education, Experience, Certificate


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 1


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'title_ar', 'years_of_experience', 'is_active')
    inlines = [EducationInline, ExperienceInline, CertificateInline]

