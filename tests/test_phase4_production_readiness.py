import threading
import time as pytime
from datetime import date, time, timedelta
from io import BytesIO
from PIL import Image

from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, transaction

from apps.accounts.models import CustomUser
from apps.clinics.models import Clinic, ClinicBranch, WorkingHours
from apps.services.models import ServiceCategory, MedicalService
from apps.appointments.models import Patient, Appointment, AppointmentStatusHistory
from apps.appointments.services import create_appointment_request, update_appointment_status_safe, get_available_slots
from apps.core.models import SiteSettings, ActivityLog
from apps.core.validators import validate_image_file
from apps.core.encryption import encrypt_text, decrypt_text, compute_search_token, get_encryption_key


class Phase4ProductionReadinessTests(TransactionTestCase):
    """
    TransactionTestCase allows testing real concurrent database transactions and row-level locking.
    """
    def setUp(self):
        cache.clear()
        self.clinic = Clinic.objects.create(name_ar='عيادة المرحلة الرابعة')
        self.branch1 = ClinicBranch.objects.create(clinic=self.clinic, name_ar='فرع صنعاء 1', is_active=True)
        self.branch2 = ClinicBranch.objects.create(clinic=self.clinic, name_ar='فرع صنعاء 2', is_active=True)

        for b in [self.branch1, self.branch2]:
            for d in range(7):
                WorkingHours.objects.create(
                    branch=b,
                    day_of_week=d,
                    morning_start=time(9, 0),
                    morning_end=time(13, 0),
                    slot_duration_minutes=30,
                    is_closed=(d == 6)
                )

        self.staff_user = CustomUser.objects.create_user(
            username='staff_pilot_tester',
            email='staff_pilot@test.com',
            password='testpassword123',
            role=CustomUser.Role.RECEPTIONIST,
            is_staff=True
        )

    def test_concurrent_confirmation_conflict_handling(self):
        """
        Tests two concurrent threads trying to confirm conflicting appointments at the same time.
        One thread MUST succeed and the other MUST raise ValidationError.
        """
        target_date = date.today() + timedelta(days=4)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        apt1 = Appointment.objects.create(
            patient=Patient.objects.create(full_name='مريض تزامن 1', phone_number='+967 770 111 001'),
            branch=self.branch1,
            appointment_date=target_date,
            appointment_time=time(9, 30),
            duration_minutes=30,
            status=Appointment.Status.PENDING
        )
        apt2 = Appointment.objects.create(
            patient=Patient.objects.create(full_name='مريض تزامن 2', phone_number='+967 770 111 002'),
            branch=self.branch1,
            appointment_date=target_date,
            appointment_time=time(9, 30),
            duration_minutes=30,
            status=Appointment.Status.PENDING
        )

        results = []
        errors = []

        def confirm_worker(apt_id):
            try:
                # Open separate database connection context per thread
                update_appointment_status_safe(apt_id, Appointment.Status.CONFIRMED, self.staff_user)
                results.append(apt_id)
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=confirm_worker, args=(apt1.id,))
        t2 = threading.Thread(target=confirm_worker, args=(apt2.id,))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Exactly ONE appointment confirmed, and ONE rejected with conflict
        self.assertEqual(len(results), 1, "Expected exactly 1 confirmed appointment")
        self.assertEqual(len(errors), 1, "Expected exactly 1 conflict rejection")
        self.assertIsInstance(errors[0], ValidationError)

    def test_activity_log_privacy_no_patient_names_or_notes_leak(self):
        """
        Verifies that booking requests and administrative actions never leak
        patient names or private clinical notes into ActivityLog.details.
        """
        target_date = date.today() + timedelta(days=3)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        c = Client()
        post_data = {
            'full_name': 'المريض السري جداً فلان بن فلان',
            'phone_number': '+967 770 999 123',
            'email': 'secret@example.com',
            'branch': self.branch1.id,
            'appointment_date': target_date.strftime('%Y-%m-%d'),
            'appointment_time': '10:00:00',
            'visit_reason': 'شكوى شديدة بالركبة والورك',
            'patient_notes': 'معلومات تشخيصية شديدة الحساسية والسرية'
        }
        res = c.post(reverse('public:booking'), post_data)
        self.assertEqual(res.status_code, 302)

        # Inspect latest ActivityLog
        latest_log = ActivityLog.objects.order_by('-id').first()
        self.assertIsNotNone(latest_log)
        self.assertNotIn('المريض السري جداً', latest_log.details, "Patient name LEAKED into ActivityLog!")
        self.assertNotIn('معلومات تشخيصية شديدة الحساسية', latest_log.details, "Patient notes LEAKED into ActivityLog!")
        self.assertIn('رمز مرجعي', latest_log.details)

    def test_fernet_cryptography_and_key_isolation(self):
        """
        Verifies that Fernet encryption uses AES-128-CBC + HMAC-SHA256,
        and that decrypting with an incorrect key fails securely.
        """
        from cryptography.fernet import Fernet, InvalidToken

        plain_text = "ملف طبي خاص للمريض محمد أحمد"
        token = encrypt_text(plain_text)
        self.assertTrue(token.startswith('gAAAAA'))

        # Correct decryption
        decrypted = decrypt_text(token)
        self.assertEqual(decrypted, plain_text)

        # Attempt decryption with an unauthorized foreign key
        foreign_key = Fernet.generate_key()
        foreign_fernet = Fernet(foreign_key)
        with self.assertRaises(InvalidToken):
            foreign_fernet.decrypt(token.encode('utf-8'))

    def test_svg_and_malicious_upload_rejection(self):
        """
        Verifies that SVG files (Stored XSS vector) and fake polyglot images are strictly rejected.
        """
        # SVG rejection
        svg = SimpleUploadedFile("danger.svg", b"<svg onload=alert(1)></svg>", content_type="image/svg+xml")
        with self.assertRaises(ValidationError) as ctx:
            validate_image_file(svg)
        self.assertIn('SVG غير مقبولة', str(ctx.exception))

        # Script-injected PNG rejection
        bad_png = SimpleUploadedFile("bad.png", b"<?php echo 'hack'; ?>", content_type="image/png")
        with self.assertRaises(ValidationError):
            validate_image_file(bad_png)

        # Valid PNG acceptance
        img = Image.new('RGB', (50, 50), color='white')
        buf = BytesIO()
        img.save(buf, format='PNG')
        good_png = SimpleUploadedFile("clean.png", buf.getvalue(), content_type="image/png")
        try:
            validate_image_file(good_png)
        except ValidationError:
            self.fail("validate_image_file rejected a clean PNG unexpectedly")

