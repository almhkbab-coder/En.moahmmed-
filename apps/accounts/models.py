from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.validators import validate_image_file


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('يجب توفير البريد الإلكتروني'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.SUPER_ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('يجب أن يكون المشرف العام staff.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('يجب أن يكون المشرف العام superuser.'))

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', _('مدير النظام الرئيسي')
        DOCTOR = 'doctor', _('طبيب')
        RECEPTIONIST = 'receptionist', _('موظف استقبال')
        CONTENT_MANAGER = 'content_manager', _('مدير محتوى')

    email = models.EmailField(_('البريد الإلكتروني'), unique=True)
    role = models.CharField(
        _('الدور الوظيفي'),
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONIST
    )
    phone_number = models.CharField(_('رقم الهاتف'), max_length=25, blank=True)
    profile_image = models.ImageField(_('الصورة الشخصية'), upload_to='users/profiles/', blank=True, null=True, validators=[validate_image_file])

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        ordering = ['-date_joined']

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username

    @property
    def is_super_admin(self):
        return self.is_superuser or self.role == self.Role.SUPER_ADMIN

    @property
    def is_doctor_role(self):
        return self.role == self.Role.DOCTOR or self.is_superuser

    @property
    def is_receptionist_role(self):
        return self.role in [self.Role.RECEPTIONIST, self.Role.SUPER_ADMIN] or self.is_superuser

    @property
    def is_content_manager_role(self):
        return self.role in [self.Role.CONTENT_MANAGER, self.Role.SUPER_ADMIN] or self.is_superuser

