from django.contrib import admin
from .models import ServiceCategory, MedicalService


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'order', 'is_active')
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(MedicalService)
class MedicalServiceAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'category', 'is_featured', 'is_active', 'order')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('title_ar', 'title_en', 'short_desc_ar')
    prepopulated_fields = {'slug': ('title_en',)}

