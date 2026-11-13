from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .validators import validate_image_file


class SiteSettings(models.Model):
    """
    Singleton model for global clinic and doctor website settings.
    """
    clinic_name_ar = models.CharField(_('اسم العيادة (عربي)'), max_length=200, default='عيادة الدكتور محمد الصياد')
    clinic_name_en = models.CharField(_('اسم العيادة (إنجليزي)'), max_length=200, default='Dr. Mohammed Al-Sayyad Clinic')
    
    doctor_name_ar = models.CharField(_('اسم الطبيب (عربي)'), max_length=200, default='الدكتور محمد الصياد')
    doctor_name_en = models.CharField(_('اسم الطبيب (إنجليزي)'), max_length=200, default='Dr. Mohammed Al-Sayyad')
    
    title_ar = models.CharField(_('اللقب المهني (عربي)'), max_length=250, default='استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية')
    title_en = models.CharField(_('اللقب المهني (إنجليزي)'), max_length=250, default='Consultant in Orthopedic Surgery, Trauma, Pelvis & Artificial Joints')
    
    specialty_ar = models.CharField(_('التخصص (عربي)'), max_length=250, default='استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية')
    specialty_en = models.CharField(_('التخصص (إنجليزي)'), max_length=250, default='Orthopedic Surgery, Trauma, Pelvis and Artificial Joint Replacement')
    
    phone = models.CharField(_('رقم الهاتف الرئيسي'), max_length=50, default='783517733')
    mobile = models.CharField(_('رقم الجوال'), max_length=50, blank=True, default='783517733')
    whatsapp = models.CharField(_('رقم الواتساب'), max_length=50, default='+967783517733')
    email = models.EmailField(_('البريد الإلكتروني للعيادة'), default='info@alsayyad-clinic.ye')
    
    address_ar = models.CharField(_('العنوان (عربي)'), max_length=300, default='صنعاء – شارع خولان – عمارة الحبيشي – بجوار مستشفى الثورة – مركز الرازي الطبي')
    address_en = models.CharField(_('العنوان (إنجليزي)'), max_length=300, default="Sana'a - Khawlan St. - Al-Hubaishi Bldg. - Next to Al-Thawra Hospital - Al-Razi Medical Center")
    
    working_hours_summary_ar = models.CharField(_('ملخص أوقات الدوام (عربي)'), max_length=255, default='السبت - الخميس: 9:00 ص - 1:00 م | 4:00 م - 8:30 م')
    working_hours_summary_en = models.CharField(_('ملخص أوقات الدوام (إنجليزي)'), max_length=255, default='Sat - Thu: 9:00 AM - 1:00 PM | 4:00 PM - 8:30 PM')
    
    logo = models.ImageField(_('شعار العيادة'), upload_to='branding/', blank=True, null=True, validators=[validate_image_file])
    favicon = models.ImageField(_('أيقونة الموقع (Favicon)'), upload_to='branding/', blank=True, null=True, validators=[validate_image_file])
    
    # Social links
    facebook_url = models.URLField(_('رابط فيسبوك'), blank=True, default='')
    x_url = models.URLField(_('رابط منصة إكس (تويتر)'), blank=True, default='')
    youtube_url = models.URLField(_('رابط قناة يوتيوب'), blank=True, default='')
    instagram_url = models.URLField(_('رابط انستغرام'), blank=True, default='')
    
    # SEO Defaults
    meta_title_ar = models.CharField(_('عنوان الموقع للبحث (عربي)'), max_length=255, default='الدكتور محمد الصياد | استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية - صنعاء')
    meta_title_en = models.CharField(_('عنوان الموقع للبحث (إنجليزي)'), max_length=255, default='Dr. Mohammed Al-Sayyad | Consultant Orthopedic, Trauma, Pelvis & Joint Replacement Surgeon - Sanaa')
    meta_description_ar = models.TextField(_('وصف الموقع للبحث (عربي)'), default='الموقع الرسمي للدكتور محمد الصياد - استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية، وأستاذ بكلية الطب جامعة صنعاء. مركز الرازي الطبي، شارع خولان، صنعاء.')
    meta_description_en = models.TextField(_('وصف الموقع للبحث (إنجليزي)'), default='Official website of Dr. Mohammed Al-Sayyad, Consultant Orthopedic, Trauma, Pelvis and Joint Replacement Surgeon, Professor at Sanaa University. Al-Razi Medical Center, Khawlan St., Sanaa.')

    class Meta:
        verbose_name = _('إعدادات الموقع العامة')
        verbose_name_plural = _('إعدادات الموقع العامة')

    def __str__(self):
        return f"{self.clinic_name_ar} - {self.doctor_name_ar}"

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('المستخدم'))
    action = models.CharField(_('العملية'), max_length=100)
    target_model = models.CharField(_('النموذج'), max_length=100, blank=True)
    target_id = models.CharField(_('المعرف'), max_length=100, blank=True)
    details = models.TextField(_('التفاصيل'), blank=True)
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    created_at = models.DateTimeField(_('وقت العملية'), auto_now_add=True)

    class Meta:
        verbose_name = _('سجل النشاط')
        verbose_name_plural = _('سجلات الأنشطة')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

