from django.contrib import admin
from .models import ArticleCategory, ArticleTag, Article


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'is_active')
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(ArticleTag)
class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name_en')
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'category', 'is_published', 'published_at', 'reading_time', 'view_count')
    list_filter = ('category', 'is_published', 'published_at')
    search_fields = ('title_ar', 'title_en', 'content_ar')
    prepopulated_fields = {'slug': ('title_en',)}

