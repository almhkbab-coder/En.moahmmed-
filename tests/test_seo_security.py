import os
from datetime import date, time, timedelta
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser
from apps.clinics.models import Clinic, ClinicBranch
from apps.appointments.models import Patient, Appointment
from apps.contact.forms import ContactForm
from apps.core.models import SiteSettings
from apps.core.validators import validate_image_file
from apps.core.views_public import check_rate_limit


class SeoAndSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.factory = RequestFactory()
        SiteSettings.get_settings()

        self.clinic = Clinic.objects.create(name_ar='عيادة الأمان التجريبية')
        self.branch = ClinicBranch.objects.create(
            clinic=self.clinic,
            name_ar='فرع صنعاء الآمن',
            is_active=True
        )

    def test_robots_txt_endpoint(self):
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        content = response.content.decode('utf-8')
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('Disallow: /dashboard/', content)
        self.assertIn('Sitemap:', content)

    def test_sitemap_xml_endpoint(self):
        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('xml', response['Content-Type'])

    def test_contact_form_honeypot_spam_rejected(self):
        form_data = {
            'full_name': 'محتال سبام',
            'phone': '123456789',
            'subject': 'إعلان غير مرغوب',
            'message': 'رسالة آلية سبام',
            'website_hp': 'http://spambot-link.com'  # Honeypot filled
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('إجراء أمني', str(form.errors))

    def test_contact_form_valid(self):
        form_data = {
            'full_name': 'مريض حقيقي',
            'phone': '777123456',
            'subject': 'استفسار عن موعد',
            'message': 'أرغب في معرفة تكلفة فحص الأشعة',
            'website_hp': ''  # Honeypot empty
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_public_homepage_renders(self):
        response = self.client.get(reverse('public:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'الدكتور محمد')

    def test_booking_status_privacy_leak_protection(self):
        patient = Patient.objects.create(
            full_name='علي محمد حسن المقطري',
            phone_number='777888999'
        )
        apt = Appointment.objects.create(
            patient=patient,
            branch=self.branch,
            appointment_date=date.today() + timedelta(days=3),
            appointment_time=time(10, 0),
            staff_notes='ملاحظة داخلية حساسة جداً لا يجب أن يراها المريض'
        )
        ref = apt.booking_reference

        # 1. Searching by phone number alone MUST FAIL to prevent patient phone enumeration
        res_phone_only = self.client.get(reverse('public:booking_status'), {'phone': '777888999'})
        self.assertIsNone(res_phone_only.context['appointment'])
        self.assertContains(res_phone_only, 'خصوصية المرضى')

        # 2. Searching by ref alone MUST FAIL to prevent reference brute-forcing
        res_ref_only = self.client.get(reverse('public:booking_status'), {'ref': ref})
        self.assertIsNone(res_ref_only.context['appointment'])

        # 3. Searching with short prefix (<8 chars) MUST FAIL
        res_short = self.client.get(reverse('public:booking_status'), {'ref': 'APT-12', 'phone': '777888999'})
        self.assertIsNone(res_short.context['appointment'])

        # 4. Searching with mismatching phone MUST FAIL
        res_mismatch = self.client.get(reverse('public:booking_status'), {'ref': ref, 'phone': '777000000'})
        self.assertIsNone(res_mismatch.context['appointment'])

        # 5. Searching with matching full ref AND matching phone SUCCEEDS with masked name and NO staff notes
        res_success = self.client.get(reverse('public:booking_status'), {'ref': ref, 'phone': '777888999'})
        self.assertEqual(res_success.status_code, 200)
        self.assertIsNotNone(res_success.context['appointment'])
        self.assertEqual(res_success.context['masked_name'], 'علي م. ح. ا.')
        self.assertContains(res_success, 'علي م. ح. ا.')
        self.assertNotContains(res_success, 'علي محمد حسن المقطري')
        self.assertNotContains(res_success, 'ملاحظة داخلية حساسة جداً لا يجب أن يراها المريض')

    def test_file_upload_validator_size_and_extension(self):
        from io import BytesIO
        from PIL import Image

        # 1. Reject executable extension
        bad_file = SimpleUploadedFile("malware.php", b"<?php echo 1; ?>", content_type="application/x-php")
        with self.assertRaises(ValidationError) as ctx:
            validate_image_file(bad_file)
        self.assertIn('نوع الملف غير مدعوم', str(ctx.exception))

        # 2. Reject SVG files strictly to prevent Stored XSS and XML attacks
        svg_file = SimpleUploadedFile("vector.svg", b"<svg><script>alert(1)</script></svg>", content_type="image/svg+xml")
        with self.assertRaises(ValidationError) as ctx:
            validate_image_file(svg_file)
        self.assertIn('SVG غير مقبولة', str(ctx.exception))

        # 3. Reject fake polyglot/script image
        fake_image = SimpleUploadedFile("bad_image.png", b"<script>alert('xss')</script>" + b"0"*100, content_type="image/png")
        with self.assertRaises(ValidationError):
            validate_image_file(fake_image)

        # 4. Reject file larger than 5MB
        huge_file = SimpleUploadedFile("giant.png", b"0" * (6 * 1024 * 1024), content_type="image/png")
        with self.assertRaises(ValidationError) as ctx:
            validate_image_file(huge_file)
        self.assertIn('5 ميجابايت', str(ctx.exception))

        # 5. Accept genuine raster PNG created with Pillow
        img = Image.new('RGB', (60, 60), color='green')
        buf = BytesIO()
        img.save(buf, format='PNG')
        good_file = SimpleUploadedFile("avatar.png", buf.getvalue(), content_type="image/png")
        try:
            validate_image_file(good_file)
        except ValidationError:
            self.fail("validate_image_file raised ValidationError unexpectedly for genuine PNG!")

    def test_rate_limiter_functionality(self):
        req = self.factory.get('/some-path/')
        req.META['REMOTE_ADDR'] = '192.168.1.100'

        # First 2 should be allowed
        self.assertTrue(check_rate_limit(req, 'test_action', max_requests=2, timeout_seconds=60))
        self.assertTrue(check_rate_limit(req, 'test_action', max_requests=2, timeout_seconds=60))

        # 3rd should be blocked
        self.assertFalse(check_rate_limit(req, 'test_action', max_requests=2, timeout_seconds=60))

