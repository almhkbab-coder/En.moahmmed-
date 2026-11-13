from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    full_name = models.CharField(_('الاسم الكامل'), max_length=150)
    phone = models.CharField(_('رقم الهاتف'), max_length=30)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True, null=True)
    subject = models.CharField(_('موضوع الرسالة'), max_length=200)
    message = models.TextField(_('نص الرسالة أو الاستفسار'))
    is_read = models.BooleanField(_('تمت القراءة'), default=False)
    replied = models.BooleanField(_('تم الرد'), default=False)
    admin_notes = models.TextField(_('ملاحظات الإدارة'), blank=True)
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاريخ الإرسال'), auto_now_add=True)

    class Meta:
        verbose_name = _('رسالة تواصل')
        verbose_name_plural = _('رسائل واستفسارات الزوار')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

