import uuid
from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.clinics.models import ClinicBranch
from apps.services.models import MedicalService
from apps.core.encryption import EncryptedCharField, EncryptedTextField, compute_search_token


class Patient(models.Model):
    full_name = EncryptedCharField(_('اسم المريض بالكامل'), max_length=500, db_index=True)
    name_search_token = models.CharField(_('رمز البحث الأمني المشفر'), max_length=64, blank=True, db_index=True)
    phone_number = models.CharField(_('رقم الهاتف'), max_length=30, db_index=True)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True, null=True)
    notes = EncryptedTextField(_('ملاحظات خاصة بالمريض'), blank=True)
    created_at = models.DateTimeField(_('تاريخ التسجيل'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('سجل المريض')
        verbose_name_plural = _('سجلات المرضى')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    def save(self, *args, **kwargs):
        if self.full_name:
            self.name_search_token = compute_search_token(self.full_name)
        super().save(*args, **kwargs)


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('قيد المراجعة والانتظار')
        CONFIRMED = 'confirmed', _('مؤكد')
        REJECTED = 'rejected', _('مرفوض')
        CANCELLED = 'cancelled', _('ملغي')
        COMPLETED = 'completed', _('مكتمل / تمت الزيارة')
        NO_SHOW = 'no_show', _('لم يحضر')

    booking_id = models.UUIDField(_('رمز الحجز الفريد'), default=uuid.uuid4, unique=True, editable=False, db_index=True)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='appointments', verbose_name=_('المريض'))
    branch = models.ForeignKey(ClinicBranch, on_delete=models.PROTECT, related_name='appointments', verbose_name=_('فرع العيادة'))
    service = models.ForeignKey(MedicalService, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name=_('الخدمة المطلوبة'))
    
    appointment_date = models.DateField(_('تاريخ الموعد'), db_index=True)
    appointment_time = models.TimeField(_('وقت الموعد'), db_index=True)
    duration_minutes = models.PositiveIntegerField(_('مدة الموعد (بالدقائق)'), default=20)
    end_time = models.TimeField(_('وقت نهاية الموعد'), null=True, blank=True, db_index=True)
    
    visit_reason = models.CharField(_('سبب الزيارة أو الشكوى الطبية'), max_length=300, blank=True)
    patient_notes = models.TextField(_('ملاحظات المريض الإضافية'), blank=True)
    
    status = models.CharField(
        _('حالة الموعد'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    staff_notes = models.TextField(_('ملاحظات العيادة الداخلية'), blank=True)
    
    created_at = models.DateTimeField(_('وقت تقديم الطلب'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        verbose_name = _('حجز موعد')
        verbose_name_plural = _('حجوزات المواعيد')
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['branch', 'appointment_date', 'status']),
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['appointment_date', 'appointment_time', 'end_time']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['branch', 'appointment_date', 'appointment_time'],
                condition=models.Q(status='confirmed'),
                name='unique_confirmed_appointment_per_branch_slot'
            )
        ]

    def __str__(self):
        return f"حجز {self.booking_reference} - {self.patient.full_name} ({self.appointment_date} {self.appointment_time})"

    def save(self, *args, **kwargs):
        if self.appointment_date and self.appointment_time:
            start_dt = datetime.combine(self.appointment_date, self.appointment_time)
            end_dt = start_dt + timedelta(minutes=self.duration_minutes)
            self.end_time = end_dt.time()
        super().save(*args, **kwargs)

    @property
    def booking_reference(self):
        # Human friendly code derived from UUID
        return f"APT-{str(self.booking_id)[:8].upper()}"

    @property
    def status_badge_class(self):
        mapping = {
            self.Status.PENDING: 'bg-warning text-dark',
            self.Status.CONFIRMED: 'bg-success text-white',
            self.Status.REJECTED: 'bg-danger text-white',
            self.Status.CANCELLED: 'bg-secondary text-white',
            self.Status.COMPLETED: 'bg-primary text-white',
            self.Status.NO_SHOW: 'bg-dark text-white',
        }
        return mapping.get(self.status, 'bg-light text-dark')


class AppointmentStatusHistory(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='status_history', verbose_name=_('الموعد'))
    old_status = models.CharField(_('الحالة السابقة'), max_length=20, choices=Appointment.Status.choices, blank=True)
    new_status = models.CharField(_('الحالة الجديدة'), max_length=20, choices=Appointment.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('الموظف المسؤول'))
    notes = models.TextField(_('سبب أو ملاحظات التغيير'), blank=True)
    timestamp = models.DateTimeField(_('تاريخ ووقت التغيير'), auto_now_add=True)

    class Meta:
        verbose_name = _('سجل تغيير حالة الموعد')
        verbose_name_plural = _('سجلات حالات المواعيد')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.appointment.booking_reference}: {self.old_status} -> {self.new_status}"

