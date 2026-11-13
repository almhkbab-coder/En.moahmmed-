from django.db import models
from django.utils.translation import gettext_lazy as _


class Clinic(models.Model):
    name_ar = models.CharField(_('اسم العيادة (عربي)'), max_length=200, default='عيادة الدكتور محمد الصياد')
    name_en = models.CharField(_('اسم العيادة (إنجليزي)'), max_length=200, default='Dr. Mohammed Al-Sayyad Clinic')
    description_ar = models.TextField(_('نبذة عن العيادة (عربي)'), blank=True)
    description_en = models.TextField(_('نبذة عن العيادة (إنجليزي)'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('العيادة')
        verbose_name_plural = _('العيادات')

    def __str__(self):
        return self.name_ar


class ClinicBranch(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='branches', verbose_name=_('العيادة'))
    name_ar = models.CharField(_('اسم الفرع (عربي)'), max_length=200, default='الفرع الرئيسي - صنعاء')
    name_en = models.CharField(_('اسم الفرع (إنجليزي)'), max_length=200, default='Main Branch - Sanaa')
    city_ar = models.CharField(_('المدينة (عربي)'), max_length=100, default='صنعاء')
    city_en = models.CharField(_('المدينة (إنجليزي)'), max_length=100, default="Sana'a")
    address_ar = models.CharField(_('العنوان التفصيلي (عربي)'), max_length=300, default='صنعاء – شارع خولان – عمارة الحبيشي – بجوار مستشفى الثورة – مركز الرازي الطبي')
    address_en = models.CharField(_('العنوان التفصيلي (إنجليزي)'), max_length=300, default="Sana'a - Khawlan St. - Al-Hubaishi Bldg. - Next to Al-Thawra Hospital - Al-Razi Medical Center")
    
    phone = models.CharField(_('رقم الهاتف'), max_length=50, default='783517733')
    whatsapp = models.CharField(_('واتساب الفرع'), max_length=50, default='+967783517733')
    email = models.EmailField(_('البريد الإلكتروني للفرع'), default='info@alsayyad-clinic.ye')
    
    map_embed_url = models.TextField(
        _('كود تضمين خريطة جوجل (Iframe URL)'),
        blank=True,
        default='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d123150.123456!2d44.2000!3d15.3500!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMTXCsDIxJzAwLjAiTiA0NMKwMTInMDAuMCJF!5e0!3m2!1sen!2sye!4v1600000000000!5m2!1sen!2sye'
    )
    latitude = models.DecimalField(_('خط العرض'), max_digits=9, decimal_places=6, null=True, blank=True, default=15.354722)
    longitude = models.DecimalField(_('خط الطول'), max_digits=9, decimal_places=6, null=True, blank=True, default=44.206667)
    
    is_primary = models.BooleanField(_('الفرع الرئيسي'), default=True)
    is_active = models.BooleanField(_('نشط ومتاح للحجز'), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('فرع العيادة')
        verbose_name_plural = _('فروع العيادة')
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f"{self.name_ar} ({self.city_ar})"


class WorkingHours(models.Model):
    class DayOfWeek(models.IntegerChoices):
        SATURDAY = 0, _('السبت (Saturday)')
        SUNDAY = 1, _('الأحد (Sunday)')
        MONDAY = 2, _('الإثنين (Monday)')
        TUESDAY = 3, _('الثلاثاء (Tuesday)')
        WEDNESDAY = 4, _('الأربعاء (Wednesday)')
        THURSDAY = 5, _('الخميس (Thursday)')
        FRIDAY = 6, _('الجمعة (Friday)')

    branch = models.ForeignKey(ClinicBranch, on_delete=models.CASCADE, related_name='working_hours', verbose_name=_('الفرع'))
    day_of_week = models.IntegerField(_('اليوم'), choices=DayOfWeek.choices)
    
    # Morning Shift
    morning_start = models.TimeField(_('بداية الفترة الصباحية'), null=True, blank=True)
    morning_end = models.TimeField(_('نهاية الفترة الصباحية'), null=True, blank=True)
    
    # Evening Shift
    evening_start = models.TimeField(_('بداية الفترة المسائية'), null=True, blank=True)
    evening_end = models.TimeField(_('نهاية الفترة المسائية'), null=True, blank=True)
    
    slot_duration_minutes = models.PositiveIntegerField(_('مدة الموعد (بالدقائق)'), default=20)
    is_closed = models.BooleanField(_('عطلة في هذا اليوم'), default=False)

    class Meta:
        verbose_name = _('ساعات العمل')
        verbose_name_plural = _('ساعات العمل وجداول المواعيد')
        unique_together = ('branch', 'day_of_week')
        ordering = ['branch', 'day_of_week']

    def __str__(self):
        return f"{self.branch.name_ar} - {self.get_day_of_week_display()}"


class ClinicHoliday(models.Model):
    branch = models.ForeignKey(ClinicBranch, on_delete=models.CASCADE, related_name='holidays', verbose_name=_('الفرع'), null=True, blank=True)
    date = models.DateField(_('تاريخ الإجازة / العطلة'))
    reason_ar = models.CharField(_('سبب الإجازة (عربي)'), max_length=255, default='إجازة رسمية')
    reason_en = models.CharField(_('سبب الإجازة (إنجليزي)'), max_length=255, default='Official Holiday')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('إجازة استثنائية / رسمية')
        verbose_name_plural = _('الإجازات والعطلات')
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.reason_ar}"

