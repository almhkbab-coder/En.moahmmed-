import uuid
import math
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from apps.core.validators import validate_image_file


class ArticleCategory(models.Model):
    name_ar = models.CharField(_('اسم التصنيف (عربي)'), max_length=150)
    name_en = models.CharField(_('اسم التصنيف (إنجليزي)'), max_length=150)
    slug = models.SlugField(_('الرابط اللطيف (Slug)'), max_length=160, unique=True, allow_unicode=True)
    is_active = models.BooleanField(_('نشط'), default=True)

    class Meta:
        verbose_name = _('تصنيف المقالات')
        verbose_name_plural = _('تصنيفات المقالات')
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en) or f"category-{uuid.uuid4().hex[:6]}"
            self.slug = base_slug
        super().save(*args, **kwargs)


class ArticleTag(models.Model):
    name_ar = models.CharField(_('الوسم (عربي)'), max_length=100)
    name_en = models.CharField(_('الوسم (إنجليزي)'), max_length=100)
    slug = models.SlugField(_('الرابط اللطيف (Slug)'), max_length=110, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = _('وسم طبي')
        verbose_name_plural = _('الوسوم الطبية')
        ordering = ['name_ar']

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en) or f"tag-{uuid.uuid4().hex[:6]}"
            self.slug = base_slug
        super().save(*args, **kwargs)


class Article(models.Model):
    title_ar = models.CharField(_('عنوان المقال (عربي)'), max_length=255)
    title_en = models.CharField(_('عنوان المقال (إنجليزي)'), max_length=255)
    slug = models.SlugField(_('الرابط اللطيف (Slug)'), max_length=255, unique=True, allow_unicode=True)
    
    category = models.ForeignKey(ArticleCategory, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name=_('التصنيف'))
    tags = models.ManyToManyField(ArticleTag, blank=True, related_name='articles', verbose_name=_('الوسوم'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('الكاتب / المراجع الطبي'))
    
    excerpt_ar = models.TextField(_('الموجز أو المقدمة (عربي)'), help_text=_('يظهر في بطاقات المقالات'))
    excerpt_en = models.TextField(_('الموجز أو المقدمة (إنجليزي)'))
    
    content_ar = models.TextField(_('المحتوى الكامل للمقال (عربي)'))
    content_en = models.TextField(_('المحتوى الكامل للمقال (إنجليزي)'))
    
    featured_image = models.ImageField(_('الصورة البارزة'), upload_to='blog/articles/', blank=True, null=True, validators=[validate_image_file])
    reading_time = models.PositiveIntegerField(_('وقت القراءة (بالدقائق)'), default=4)
    
    is_published = models.BooleanField(_('منشور'), default=False)
    published_at = models.DateTimeField(_('تاريخ النشر'), default=timezone.now)
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    
    # Medical Disclaimer Notice
    medical_disclaimer_ar = models.TextField(
        _('إخلاء المسؤولية الطبية'),
        default='تنبيه طبي: المحتوى المنشور لأغراض تثقيفية وتوعوية فقط ولا يُعد بديلاً عن الفحص الطبي السريري أو الاستشارة الطبية المباشرة مع الطبيب المختص.'
    )
    
    # SEO
    meta_title_ar = models.CharField(_('عنوان السيو (عربي)'), max_length=255, blank=True)
    meta_title_en = models.CharField(_('عنوان السيو (إنجليزي)'), max_length=255, blank=True)
    meta_desc_ar = models.TextField(_('وصف السيو (عربي)'), blank=True)
    meta_desc_en = models.TextField(_('وصف السيو (إنجليزي)'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('مقال طبي')
        verbose_name_plural = _('المقالات الطبية والنصائح')
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_en) or f"article-{uuid.uuid4().hex[:6]}"
            self.slug = base_slug
        # Calculate reading time based on word count (approx 200 words per minute)
        total_words = len(self.content_ar.split()) + len(self.content_en.split())
        self.reading_time = max(1, math.ceil(total_words / 200)) if total_words else 3
        
        if not self.meta_title_ar:
            self.meta_title_ar = f"{self.title_ar} | عيادة الدكتور محمد الصياد"
        if not self.meta_desc_ar:
            self.meta_desc_ar = self.excerpt_ar[:160]
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('public:article_detail', kwargs={'slug': self.slug})

