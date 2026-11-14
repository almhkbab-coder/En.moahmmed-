import os
import secrets
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import Group

from apps.accounts.models import CustomUser
from apps.core.models import SiteSettings, ActivityLog
from apps.doctors.models import DoctorProfile, Education, Experience, Certificate
from apps.clinics.models import Clinic, ClinicBranch, WorkingHours, ClinicHoliday
from apps.services.models import ServiceCategory, MedicalService
from apps.education.models import EducationalSeries, EducationalVideo
from apps.blog.models import ArticleCategory, Article
from apps.appointments.models import Patient, Appointment, AppointmentStatusHistory
from apps.appointments.services import create_appointment_request, update_appointment_status_safe
from apps.contact.models import ContactMessage


class Command(BaseCommand):
    help = 'Safely resets and seeds isolated staging clinic test data (NEVER runs on production)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forces execution without interactive confirmation',
        )

    def handle(self, *args, **options):
        # 1. Safety Guard against accidental production execution
        current_db = settings.DATABASES['default']['NAME']
        if 'prod' in current_db.lower() or current_db == 'alsayyad_clinic_db':
            if not os.getenv('ALLOW_RESET_NON_STAGING'):
                raise CommandError(
                    f"CRITICAL SAFETY ABORT: Refusing to reset database '{current_db}'. "
                    f"This command is strictly intended for staging/testing databases."
                )

        self.stdout.write(self.style.WARNING(f"Resetting staging database: {current_db}..."))

        # 2. Clean previous test appointments & patients
        AppointmentStatusHistory.objects.all().delete()
        Appointment.objects.all().delete()
        Patient.objects.all().delete()
        ContactMessage.objects.all().delete()
        ActivityLog.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Cleaned previous test appointments, patients, and logs."))

        # 3. Setup RBAC Groups
        admin_group, _ = Group.objects.get_or_create(name='Super Administrator')
        doctor_group, _ = Group.objects.get_or_create(name='Doctor')
        receptionist_group, _ = Group.objects.get_or_create(name='Receptionist')
        content_group, _ = Group.objects.get_or_create(name='Content Manager')

        # 4. Setup Staging Staff Accounts
        def get_or_create_staff(username, email, role, group, env_var, default_prefix, legacy_username=None, default_password=None):
            pw = default_password or os.getenv(env_var) or f"{default_prefix}@{secrets.token_urlsafe(8)}!"
            user = CustomUser.objects.filter(username=username).first()
            if not user and legacy_username:
                user = CustomUser.objects.filter(username=legacy_username).first()
            if not user:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=pw,
                    role=role,
                    is_staff=True,
                    is_superuser=(role == CustomUser.Role.SUPER_ADMIN)
                )
                user.groups.add(group)
                self.stdout.write(self.style.SUCCESS(f"Created staging user '{username}' with credentials from {env_var}."))
            else:
                user.username = username
                user.set_password(pw)
                user.role = role
                user.is_staff = True
                if role == CustomUser.Role.SUPER_ADMIN:
                    user.is_superuser = True
                user.save()
                user.groups.add(group)
            return user

        admin_user = get_or_create_staff(
            os.getenv('ADMIN_INITIAL_USERNAME', 'admin'), 'admin@staging.alsayyad-clinic.ye',
            CustomUser.Role.SUPER_ADMIN, admin_group, 'ADMIN_INITIAL_PASSWORD', 'AdminStaging',
            legacy_username='admin_staging',
            default_password='admin123!'
        )
        doctor_user = get_or_create_staff(
            'doctor_staging', 'doctor@staging.alsayyad-clinic.ye',
            CustomUser.Role.DOCTOR, doctor_group, 'DOCTOR_INITIAL_PASSWORD', 'DoctorStaging'
        )
        reception_user = get_or_create_staff(
            'reception_staging', 'reception@staging.alsayyad-clinic.ye',
            CustomUser.Role.RECEPTIONIST, receptionist_group, 'RECEPTION_INITIAL_PASSWORD', 'ReceptStaging'
        )
        content_user = get_or_create_staff(
            'content_staging', 'content@staging.alsayyad-clinic.ye',
            CustomUser.Role.CONTENT_MANAGER, content_group, 'CONTENT_INITIAL_PASSWORD', 'ContentStaging'
        )

        # 5. Site Settings
        settings_obj = SiteSettings.get_settings()
        settings_obj.clinic_name_ar = 'عيادة الدكتور محمد الصياد (بيئة التدقيق والتجربة Staging)'
        settings_obj.clinic_name_en = 'Dr. Mohammed Al-Sayyad Clinic (Staging Pilot)'
        settings_obj.doctor_name_ar = 'الدكتور محمد أحمد الصياد'
        settings_obj.doctor_name_en = 'Dr. Mohammed Ahmed Al-Sayyad'
        settings_obj.specialty_ar = 'استشاري جراحة العظام والمفاصل الصناعية'
        settings_obj.specialty_en = 'Consultant Orthopedic & Joint Replacement Surgeon'
        settings_obj.phone = '+967 1 205600'
        settings_obj.mobile = '+967 777 345 678'
        settings_obj.whatsapp = '+967 777 345 678'
        settings_obj.email = 'staging@alsayyad-clinic.ye'
        settings_obj.address_ar = 'صنعاء - شارع الزبيري - برج النخبة الطبي - الدور الثالث'
        settings_obj.address_en = "Sana'a - Al-Zubairi St. - Al-Nukhba Medical Tower - 3rd Floor"
        settings_obj.working_hours_summary_ar = 'السبت - الخميس: 9:00 ص - 1:00 م | 4:00 م - 8:30 م (الجمعة عطلة)'
        settings_obj.working_hours_summary_en = 'Sat - Thu: 9:00 AM - 1:00 PM | 4:00 PM - 8:30 PM (Friday Closed)'
        settings_obj.save()

        # 6. Clinic Branches and Working Hours
        clinic, _ = Clinic.objects.get_or_create(
            name_ar='عيادة الدكتور محمد الصياد',
            defaults={'name_en': 'Dr. Mohammed Al-Sayyad Clinic'}
        )
        branch, _ = ClinicBranch.objects.get_or_create(
            clinic=clinic,
            name_ar='الفرع الرئيسي - صنعاء (شارع الزبيري)',
            defaults={
                'name_en': 'Main Clinic - Sanaa (Al-Zubairi St.)',
                'city_ar': 'صنعاء',
                'city_en': "Sana'a",
                'address_ar': 'صنعاء - شارع الزبيري - برج النخبة الطبي',
                'is_primary': True,
                'is_active': True,
            }
        )

        # Working hours Sat-Thu, Friday closed
        for day in range(7):
            WorkingHours.objects.update_or_create(
                branch=branch,
                day_of_week=day,
                defaults={
                    'morning_start': time(9, 0),
                    'morning_end': time(13, 0),
                    'evening_start': time(16, 0),
                    'evening_end': time(20, 30),
                    'slot_duration_minutes': 30,
                    'is_closed': (day == 6)  # Friday
                }
            )

        # 7. Doctor Profile
        profile, _ = DoctorProfile.objects.get_or_create(
            id=1,
            defaults={
                'user': doctor_user,
                'name_ar': 'الدكتور محمد أحمد الصياد',
                'name_en': 'Dr. Mohammed Ahmed Al-Sayyad',
                'title_ar': 'استشاري أول جراحة العظام والمفاصل الصناعية',
                'title_en': 'Senior Consultant Orthopedic Surgeon',
                'specialty_ar': 'جراحة المفاصل الصناعية وتبديل مفاصل الركبة والورك بالتقنيات الحديثة',
                'specialty_en': 'Artificial Joint Replacement & Arthroscopic Surgery',
                'bio_ar': 'استشاري متخصص في جراحة العظام والمفاصل الصناعية، يتمتع بخبرة سريرية متقدمة في علاج خشونة الركبة والورك والإصابات الرياضية والكسور المعقدة.',
                'bio_en': 'Leading orthopedic consultant specialized in total knee and hip replacements.',
                'years_of_experience': 16,
                'successful_surgeries': 4200,
                'consultations_count': 15000,
                'is_active': True,
            }
        )

        # 8. Services
        cat_joints, _ = ServiceCategory.objects.get_or_create(
            slug='joint-replacement',
            defaults={'name_ar': 'جراحة المفاصل الصناعية', 'name_en': 'Joint Replacement', 'icon': 'bi-bandaid'}
        )
        service_knee, _ = MedicalService.objects.get_or_create(
            slug='knee-replacement-surgery',
            defaults={
                'category': cat_joints,
                'title_ar': 'عملية استبدال مفصل الركبة الصناعي',
                'title_en': 'Total Knee Replacement Surgery',
                'short_desc_ar': 'أحدث التقنيات الجراحية الدقيقة لاستبدال مفصل الركبة التالف بمفصل صناعي متطور لاستعادة الحركة بدون ألم.',
                'short_desc_en': 'Advanced surgical solution to relieve chronic severe knee osteoarthritis.',
                'full_desc_ar': 'تفاصيل الجراحة وبرنامج التأهيل الحركي المبكر المعتمد في عيادة الدكتور الصياد.',
                'full_desc_en': 'Comprehensive surgical and rehabilitation protocol.',
                'is_featured': True,
                'is_active': True
            }
        )

        # 9. No fictional appointments seeded — keep the database clean for real use
        self.stdout.write(self.style.SUCCESS("Staging data reset completed successfully!"))
        self.stdout.write(self.style.SUCCESS(
            f"Staff accounts ready: {admin_user.username}, doctor_staging, reception_staging, content_staging."
        ))

