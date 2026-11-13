from datetime import date, time, timedelta
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser
from apps.clinics.models import Clinic, ClinicBranch, WorkingHours, ClinicHoliday
from apps.services.models import ServiceCategory, MedicalService
from apps.appointments.models import Patient, Appointment, AppointmentStatusHistory
from apps.contact.models import ContactMessage
from apps.appointments.services import (
    get_available_slots,
    create_appointment_request,
    update_appointment_status_safe
)


class AppointmentEngineTests(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(name_ar='عيادة الصياد التجريبية')
        self.branch = ClinicBranch.objects.create(
            clinic=self.clinic,
            name_ar='فرع صنعاء التجريبي',
            is_active=True
        )
        # Saturday is day 0
        for day in range(7):
            WorkingHours.objects.create(
                branch=self.branch,
                day_of_week=day,
                morning_start=time(9, 0),
                morning_end=time(13, 0),
                evening_start=time(16, 0),
                evening_end=time(20, 0),
                slot_duration_minutes=30,
                is_closed=(day == 6)  # Friday closed
            )

        self.service = MedicalService.objects.create(
            title_ar='جراحة مفصل الركبة',
            title_en='Knee Surgery',
            short_desc_ar='وصف تجريبي',
            short_desc_en='Test desc',
            full_desc_ar='تفاصيل تجريبية',
            full_desc_en='Full test desc'
        )

        self.staff_user = CustomUser.objects.create_user(
            username='reception_tester',
            email='reception@test.com',
            password='password123',
            is_staff=True
        )

    @override_settings(PUBLIC_FORMS_ENABLED=False)
    def test_preview_booking_form_does_not_store_patient_data(self):
        response = self.client.post(reverse('public:booking'), {
            'full_name': 'Preview Visitor',
            'phone_number': '+967770000000',
            'branch': self.branch.id,
            'appointment_date': '2030-01-01',
            'appointment_time': '10:00',
        })

        self.assertRedirects(response, reverse('public:booking'), fetch_redirect_response=False)
        self.assertEqual(Patient.objects.count(), 0)
        self.assertEqual(Appointment.objects.count(), 0)

    @override_settings(PUBLIC_FORMS_ENABLED=False)
    def test_preview_contact_form_does_not_store_messages(self):
        response = self.client.post(reverse('public:contact'), {
            'name': 'Preview Visitor',
            'phone': '+967770000000',
            'message': 'Preview only',
        })

        self.assertRedirects(response, reverse('public:contact'), fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_past_date_rejected(self):
        yesterday = date.today() - timedelta(days=1)
        res = get_available_slots(self.branch, yesterday)
        self.assertFalse(res['is_open'])
        self.assertIn('الماضي', res['reason'])

    def test_holiday_rejection(self):
        future_date = date.today() + timedelta(days=10)
        ClinicHoliday.objects.create(
            branch=self.branch,
            date=future_date,
            reason_ar='إجازة عيد الفطر'
        )
        res = get_available_slots(self.branch, future_date)
        self.assertFalse(res['is_open'])
        self.assertIn('عيد الفطر', res['reason'])

    def test_create_appointment_request_success(self):
        target_date = date.today() + timedelta(days=4)
        apt = create_appointment_request(
            full_name='مريض تجريبي',
            phone_number='+967 770 123 456',
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(10, 0),
            service=self.service,
            visit_reason='ألم بالركبة'
        )
        self.assertEqual(apt.status, Appointment.Status.PENDING)
        self.assertEqual(apt.patient.full_name, 'مريض تجريبي')
        self.assertEqual(apt.status_history.count(), 1)
        self.assertTrue(apt.booking_reference.startswith('APT-'))

    def test_double_booking_prevention(self):
        target_date = date.today() + timedelta(days=5)
        from apps.appointments.services import get_model_day_of_week
        # Ensure target_date is not Friday (closed)
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        # 1. Create two pending appointments for the same slot (simulating concurrent pending requests)
        patient1 = Patient.objects.create(full_name='مريض أول', phone_number='+967 770 111 111')
        patient2 = Patient.objects.create(full_name='مريض ثان', phone_number='+967 770 222 222')
        
        apt1 = Appointment.objects.create(
            patient=patient1,
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(9, 30),
            status=Appointment.Status.PENDING
        )
        apt2 = Appointment.objects.create(
            patient=patient2,
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(9, 30),
            status=Appointment.Status.PENDING
        )

        # 2. Confirm first appointment - should succeed
        update_appointment_status_safe(apt1.id, Appointment.Status.CONFIRMED, self.staff_user)

        # 3. Confirming apt2 should raise ValidationError due to conflict check
        with self.assertRaises(ValidationError):
            update_appointment_status_safe(apt2.id, Appointment.Status.CONFIRMED, self.staff_user)

        # 4. Service-level create_appointment_request also rejects already confirmed slots
        with self.assertRaises(ValidationError):
            create_appointment_request(
                full_name='مريض ثالث',
                phone_number='+967 770 444 444',
                branch=self.branch,
                appointment_date=target_date,
                appointment_time=time(9, 30),
                service=self.service
            )

        # 5. Database-level constraint: directly attempting to save a duplicate CONFIRMED appointment triggers IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Appointment.objects.create(
                patient=patient2,
                branch=self.branch,
                appointment_date=target_date,
                appointment_time=time(9, 30),
                status=Appointment.Status.CONFIRMED
            )

    def test_patient_delete_protected_when_has_appointments(self):
        from django.db.models.deletion import ProtectedError
        target_date = date.today() + timedelta(days=4)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        apt = create_appointment_request(
            full_name='مريض محمي',
            phone_number='+967 770 999 888',
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(10, 30)
        )
        with self.assertRaises(ProtectedError):
            apt.patient.delete()

    def test_past_date_creation_rejected(self):
        yesterday = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            create_appointment_request(
                full_name='مريض سابق',
                phone_number='+967 770 555 555',
                branch=self.branch,
                appointment_date=yesterday,
                appointment_time=time(10, 0)
            )

    def test_closed_day_creation_rejected(self):
        # Find next Friday
        target_date = date.today() + timedelta(days=1)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) != 6:
            target_date += timedelta(days=1)

        with self.assertRaises(ValidationError):
            create_appointment_request(
                full_name='مريض الجمعة',
                phone_number='+967 770 666 666',
                branch=self.branch,
                appointment_date=target_date,
                appointment_time=time(10, 0)
            )

    def test_outside_working_hours_rejected(self):
        target_date = date.today() + timedelta(days=3)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        # 3:00 AM is outside working hours
        with self.assertRaises(ValidationError):
            create_appointment_request(
                full_name='مريض فجر',
                phone_number='+967 770 777 777',
                branch=self.branch,
                appointment_date=target_date,
                appointment_time=time(3, 0)
            )

    def test_status_transitions_and_audit(self):
        target_date = date.today() + timedelta(days=6)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        apt = create_appointment_request(
            full_name='مريض التدقيق',
            phone_number='+967 770 333 333',
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(11, 0)
        )
        # Pending -> Confirmed
        update_appointment_status_safe(apt.id, Appointment.Status.CONFIRMED, self.staff_user, 'تأكيد هاتفي')
        # Confirmed -> Completed
        update_appointment_status_safe(apt.id, Appointment.Status.COMPLETED, self.staff_user, 'حضر المريض وتم الفحص')

        apt.refresh_from_db()
        self.assertEqual(apt.status, Appointment.Status.COMPLETED)
        self.assertEqual(apt.status_history.count(), 3)

    def test_overlapping_duration_intervals_conflict(self):
        target_date = date.today() + timedelta(days=5)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        # 1. Create and confirm appointment A: 09:00 - 09:30 (30 minutes)
        apt_a = create_appointment_request(
            full_name='مريض الفترة أ',
            phone_number='+967 770 888 111',
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(9, 0)
        )
        apt_a.duration_minutes = 30
        apt_a.save()
        update_appointment_status_safe(apt_a.id, Appointment.Status.CONFIRMED, self.staff_user)

        # 2. Overlapping appointment B: starts at 09:15 with 30 min duration (09:15 - 09:45) -> MUST BE REJECTED
        with self.assertRaises(ValidationError):
            create_appointment_request(
                full_name='مريض متداخل ب',
                phone_number='+967 770 888 222',
                branch=self.branch,
                appointment_date=target_date,
                appointment_time=time(9, 15)
            )

        # 3. Non-overlapping appointment C: starts at 09:30 with 30 min duration (09:30 - 10:00) -> MUST SUCCEED
        apt_c = create_appointment_request(
            full_name='مريض متتالي ج',
            phone_number='+967 770 888 333',
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(9, 30)
        )
        self.assertEqual(apt_c.status, Appointment.Status.PENDING)
        update_appointment_status_safe(apt_c.id, Appointment.Status.CONFIRMED, self.staff_user)
        apt_c.refresh_from_db()
        self.assertEqual(apt_c.status, Appointment.Status.CONFIRMED)

    def test_different_branches_independent_operation(self):
        target_date = date.today() + timedelta(days=4)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        branch2 = ClinicBranch.objects.create(
            clinic=self.clinic,
            name_ar='فرع عدن التجريبي',
            is_active=True
        )
        for day in range(7):
            WorkingHours.objects.create(
                branch=branch2,
                day_of_week=day,
                morning_start=time(9, 0),
                morning_end=time(13, 0),
                slot_duration_minutes=30,
                is_closed=(day == 6)
            )

        # Confirm 09:00 appointment in branch 1
        apt1 = create_appointment_request(
            full_name='مريض فرع صنعاء',
            phone_number='+967 771 111 111',
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(9, 0)
        )
        update_appointment_status_safe(apt1.id, Appointment.Status.CONFIRMED, self.staff_user)

        # Confirm identical date and time (09:00) in branch 2 -> MUST SUCCEED with zero conflict
        apt2 = create_appointment_request(
            full_name='مريض فرع عدن',
            phone_number='+967 772 222 222',
            branch=branch2,
            appointment_date=target_date,
            appointment_time=time(9, 0)
        )
        update_appointment_status_safe(apt2.id, Appointment.Status.CONFIRMED, self.staff_user)
        apt2.refresh_from_db()
        self.assertEqual(apt2.status, Appointment.Status.CONFIRMED)

    def test_cancelled_and_rejected_release_slot(self):
        target_date = date.today() + timedelta(days=5)
        from apps.appointments.services import get_model_day_of_week
        while get_model_day_of_week(target_date) == 6:
            target_date += timedelta(days=1)

        # Book and confirm 10:00 slot
        apt = create_appointment_request(
            full_name='مريض إلغاء',
            phone_number='+967 773 333 333',
            branch=self.branch,
            appointment_date=target_date,
            appointment_time=time(10, 0)
        )
        update_appointment_status_safe(apt.id, Appointment.Status.CONFIRMED, self.staff_user)

        # In get_available_slots, 10:00 is booked
        res_booked = get_available_slots(self.branch, target_date)
        slot_10 = next((s for s in res_booked['slots'] if s['time'] == '10:00:00'), None)
        self.assertIsNotNone(slot_10)
        self.assertTrue(slot_10['is_booked'])
        self.assertFalse(slot_10['is_available'])

        # Now cancel the appointment
        update_appointment_status_safe(apt.id, Appointment.Status.CANCELLED, self.staff_user, 'اعتذر المريض')

        # Slot 10:00 MUST BE RELEASED and available again
        res_freed = get_available_slots(self.branch, target_date)
        slot_freed = next((s for s in res_freed['slots'] if s['time'] == '10:00:00'), None)
        self.assertIsNotNone(slot_freed)
        self.assertFalse(slot_freed['is_booked'])
        self.assertTrue(slot_freed['is_available'])

    def test_patient_data_encryption_at_rest(self):
        from django.db import connection
        from apps.core.encryption import compute_search_token

        patient = Patient.objects.create(
            full_name='أحمد بن علي الشامي',
            phone_number='+967 779 888 777',
            notes='تقرير طبي تشخيصي سري للغاية'
        )

        # 1. Model transparently returns decrypted plaintext
        self.assertEqual(patient.full_name, 'أحمد بن علي الشامي')
        self.assertEqual(patient.notes, 'تقرير طبي تشخيصي سري للغاية')

        # 2. Raw database record stores Fernet ciphertext starting with 'gAAAAA'
        with connection.cursor() as cursor:
            cursor.execute("SELECT full_name, notes, name_search_token FROM appointments_patient WHERE id = %s", [patient.id])
            row = cursor.fetchone()
            db_full_name, db_notes, db_token = row[0], row[1], row[2]

            self.assertTrue(db_full_name.startswith('gAAAAA'), "full_name in PostgreSQL is NOT encrypted!")
            self.assertTrue(db_notes.startswith('gAAAAA'), "notes in PostgreSQL is NOT encrypted!")
            self.assertNotIn('أحمد بن علي الشامي', db_full_name, "Plaintext patient name leaked in raw DB!")
            self.assertEqual(db_token, compute_search_token('أحمد بن علي الشامي'))

