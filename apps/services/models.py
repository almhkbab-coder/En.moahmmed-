from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import uuid
from apps.core.validators import validate_image_file


class ServiceCategory(models.Model):
    name_ar = models.CharField(_('اسم التصنيف (عربي)'), max_length=150)
    name_en = models.CharField(_('اسم التصنيف (إنجليزي)'), max_length=150)
    slug = models.SlugField(_('الرابط اللطيف (Slug)'), max_length=160, unique=True, allow_unicode=True)
    icon = models.CharField(_('أيقونة التصنيف (Bootstrap Icon)'), max_length=50, default='bi-heart-pulse')
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    is_active = models.BooleanField(_('نشط'), default=True)

    class Meta:
        verbose_name = _('تصنيف الخدمات الطبية')
        verbose_name_plural = _('تصنيفات الخدمات الطبية')
        ordering = ['order', 'id']

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en) or f"category-{uuid.uuid4().hex[:6]}"
            self.slug = base_slug
        super().save(*args, **kwargs)


class MedicalService(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='services', verbose_name=_('التصنيف'))
    title_ar = models.CharField(_('عنوان الخدمة (عربي)'), max_length=255)
    title_en = models.CharField(_('عنوان الخدمة (إنجليزي)'), max_length=255)
    slug = models.SlugField(_('الرابط اللطيف (Slug)'), max_length=255, unique=True, allow_unicode=True)
    
    short_desc_ar = models.TextField(_('نبذة مختصرة (عربي)'), help_text=_('تظهر في بطاقات الخدمات والواجهة الرئيسية'))
    short_desc_en = models.TextField(_('نبذة مختصرة (إنجليزي)'))
    
    full_desc_ar = models.TextField(_('التفاصيل الكاملة للجراحة أو العلاج (عربي)'))
    full_desc_en = models.TextField(_('التفاصيل الكاملة للجراحة أو العلاج (إنجليزي)'))
    
    featured_image = models.ImageField(_('الصورة المميزة للخدمة'), upload_to='services/', blank=True, null=True, validators=[validate_image_file])
    icon = models.CharField(_('أيقونة الخدمة (Bootstrap Icon)'), max_length=50, default='bi-shield-plus')
    
    is_featured = models.BooleanField(_('خدمة مميزة في الواجهة الرئيسية'), default=False)
    is_active = models.BooleanField(_('نشطة ومعروضة للمرضى'), default=True)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    
    # SEO Metadata
    meta_title_ar = models.CharField(_('عنوان السيو (عربي)'), max_length=255, blank=True)
    meta_title_en = models.CharField(_('عنوان السيو (إنجليزي)'), max_length=255, blank=True)
    meta_desc_ar = models.TextField(_('وصف السيو (عربي)'), blank=True)
    meta_desc_en = models.TextField(_('وصف السيو (إنجليزي)'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('خدمة طبية / عملية جراحية')
        verbose_name_plural = _('الخدمات الطبية والعمليات الجراحية')
        ordering = ['order', '-is_featured', 'id']

    def __str__(self):
        return self.title_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_en)
            if not base_slug:
                base_slug = f"service-{uuid.uuid4().hex[:6]}"
            self.slug = base_slug
        if not self.meta_title_ar:
            self.meta_title_ar = f"{self.title_ar} | عيادة الدكتور محمد الصياد"
        if not self.meta_title_en:
            self.meta_title_en = f"{self.title_en} | Dr. Mohammed Al-Sayyad Clinic"
        if not self.meta_desc_ar:
            self.meta_desc_ar = self.short_desc_ar[:160]
        if not self.meta_desc_en:
            self.meta_desc_en = self.short_desc_en[:160]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('public:service_detail', kwargs={'slug': self.slug})

