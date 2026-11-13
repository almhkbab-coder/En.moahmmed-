from django.contrib import admin
from .models import EducationalSeries, EducationalVideo


class EducationalVideoInline(admin.TabularInline):
    model = EducationalVideo
    extra = 1
    fields = ('episode_number', 'title_ar', 'youtube_url', 'duration_minutes', 'is_published')


@admin.register(EducationalSeries)
class EducationalSeriesAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'title_en', 'episode_count', 'order', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title_ar', 'title_en', 'description_ar')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [EducationalVideoInline]


@admin.register(EducationalVideo)
class EducationalVideoAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'series', 'episode_number', 'duration_minutes', 'is_published')
    list_filter = ('series', 'is_published')
    search_fields = ('title_ar', 'title_en', 'youtube_video_id')
    prepopulated_fields = {'slug': ('title_en',)}

