from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from apps.accounts.models import CustomUser


class AuthenticationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.super_admin = CustomUser.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            role=CustomUser.Role.SUPER_ADMIN
        )
        self.doctor = CustomUser.objects.create_user(
            username='doctor_test',
            email='doctor@test.com',
            password='testpassword123',
            role=CustomUser.Role.DOCTOR,
            is_staff=True
        )
        self.receptionist = CustomUser.objects.create_user(
            username='reception_test',
            email='reception@test.com',
            password='testpassword123',
            role=CustomUser.Role.RECEPTIONIST,
            is_staff=True
        )
        self.content_mgr = CustomUser.objects.create_user(
            username='content_test',
            email='content@test.com',
            password='testpassword123',
            role=CustomUser.Role.CONTENT_MANAGER,
            is_staff=True
        )

    def test_login_successful(self):
        response = self.client.post(reverse('dashboard:login'), {
            'username': 'doctor_test',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('dashboard:index'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('dashboard:login'), {
            'username': 'doctor_test',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(response, 'غير صحيحة')

    def test_logout(self):
        self.client.login(username='doctor_test', password='testpassword123')
        response = self.client.get(reverse('dashboard:logout'))
        self.assertRedirects(response, reverse('dashboard:login'))
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_unauthorized_dashboard_access_redirects(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(response, f"{reverse('dashboard:login')}?next={reverse('dashboard:index')}")

    def test_super_admin_has_full_access(self):
        self.client.login(username='admin_test', password='testpassword123')
        views_to_test = [
            'dashboard:index',
            'dashboard:appointments_list',
            'dashboard:appointments_calendar',
            'dashboard:patients_list',
            'dashboard:services_list',
            'dashboard:education_series_list',
            'dashboard:articles_list',
            'dashboard:doctor_profile',
            'dashboard:site_settings',
            'dashboard:contact_messages',
            'dashboard:activity_logs',
        ]
        for v_name in views_to_test:
            res = self.client.get(reverse(v_name))
            self.assertEqual(res.status_code, 200, f"Super admin failed on view {v_name}")

    def test_receptionist_rbac_least_privilege(self):
        self.client.login(username='reception_test', password='testpassword123')
        # Allowed views for receptionist
        allowed_views = [
            'dashboard:index',
            'dashboard:appointments_list',
            'dashboard:appointments_calendar',
            'dashboard:patients_list',
            'dashboard:contact_messages',
        ]
        for v_name in allowed_views:
            res = self.client.get(reverse(v_name))
            self.assertEqual(res.status_code, 200, f"Receptionist should have access to {v_name}")

        # Forbidden views for receptionist (must return 403)
        forbidden_views = [
            'dashboard:site_settings',
            'dashboard:doctor_profile',
            'dashboard:services_list',
            'dashboard:articles_list',
            'dashboard:activity_logs',
        ]
        for v_name in forbidden_views:
            res = self.client.get(reverse(v_name))
            self.assertEqual(res.status_code, 403, f"Receptionist must be blocked with 403 on {v_name}")

    def test_content_manager_rbac_least_privilege(self):
        self.client.login(username='content_test', password='testpassword123')
        # Allowed views for content manager
        allowed_views = [
            'dashboard:index',
            'dashboard:services_list',
            'dashboard:education_series_list',
            'dashboard:articles_list',
        ]
        for v_name in allowed_views:
            res = self.client.get(reverse(v_name))
            self.assertEqual(res.status_code, 200, f"Content Manager should access {v_name}")

        # Forbidden views for content manager
        forbidden_views = [
            'dashboard:appointments_list',
            'dashboard:patients_list',
            'dashboard:site_settings',
            'dashboard:activity_logs',
        ]
        for v_name in forbidden_views:
            res = self.client.get(reverse(v_name))
            self.assertEqual(res.status_code, 403, f"Content Manager must be blocked with 403 on {v_name}")

    def test_doctor_rbac(self):
        self.client.login(username='doctor_test', password='testpassword123')
        # Doctor can manage profile, appointments, services, articles
        res_profile = self.client.get(reverse('dashboard:doctor_profile'))
        self.assertEqual(res_profile.status_code, 200)

        # Doctor cannot change global system settings or view security audit logs
        res_settings = self.client.get(reverse('dashboard:site_settings'))
        self.assertEqual(res_settings.status_code, 403)

        res_logs = self.client.get(reverse('dashboard:activity_logs'))
        self.assertEqual(res_logs.status_code, 403)

    def test_login_brute_force_lockout(self):
        # 5 failed attempts
        for _ in range(5):
            res = self.client.post(reverse('dashboard:login'), {
                'username': 'reception_test',
                'password': 'badpassword'
            })
            self.assertEqual(res.status_code, 200)

        # 6th attempt should be locked out (429 Too Many Requests)
        res_locked = self.client.post(reverse('dashboard:login'), {
            'username': 'reception_test',
            'password': 'testpassword123'
        })
        self.assertEqual(res_locked.status_code, 429)
        self.assertContains(res_locked, 'حظر تسجيل الدخول مؤقتاً', status_code=429)
