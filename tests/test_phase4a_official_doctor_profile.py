from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from apps.core.models import SiteSettings
from apps.doctors.models import DoctorProfile, Education, Experience
from apps.services.models import MedicalService, ServiceCategory
from apps.clinics.models import Clinic, ClinicBranch


class OfficialDoctorProfilePhase4ATests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()

        # Ensure SiteSettings with official data
        self.settings = SiteSettings.get_settings()
        self.settings.doctor_name_ar = "الدكتور محمد الصياد"
        self.settings.doctor_name_en = "Dr. Mohammed Al-Sayyad"
        self.settings.title_ar = "استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية"
        self.settings.title_en = "Consultant in Orthopedic Surgery, Trauma, Pelvis & Artificial Joints"
        self.settings.phone = "783517733"
        self.settings.whatsapp = "+967783517733"
        self.settings.address_ar = "صنعاء – شارع خولان – عمارة الحبيشي – بجوار مستشفى الثورة – مركز الرازي الطبي"
        self.settings.address_en = "Sana'a - Khawlan St. - Al-Hubaishi Bldg. - Next to Al-Thawra Hospital - Al-Razi Medical Center"
        self.settings.save()

        # Clinic & Primary Branch
        self.clinic = Clinic.objects.create(name_ar="عيادة الدكتور محمد الصياد")
        self.branch = ClinicBranch.objects.create(
            clinic=self.clinic,
            name_ar="الفرع الرئيسي - مركز الرازي الطبي",
            address_ar="صنعاء – شارع خولان – عمارة الحبيشي – بجوار مستشفى الثورة – مركز الرازي الطبي",
            phone="783517733",
            whatsapp="+967783517733",
            is_primary=True,
            is_active=True
        )

        # Official DoctorProfile
        self.doctor = DoctorProfile.objects.create(
            name_ar="الدكتور محمد الصياد",
            name_en="Dr. Mohammed Al-Sayyad",
            title_ar="استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية",
            title_en="Consultant in Orthopedic Surgery, Trauma, Pelvis & Artificial Joints",
            specialty_ar="استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية",
            bio_ar=(
                "الدكتور محمد الصياد استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية، "
                "وأستاذ جراحة العظام بكلية الطب – جامعة صنعاء، يمتلك خلفية علمية وتخصصية متقدمة في مجال جراحة العظام، "
                "مع اهتمام خاص بجراحات استبدال المفاصل الصناعية للركبة والحوض، وتقنيات المفاصل الصناعية باستخدام الروبوت.\n\n"
                "كما يعمل مدرباً معتمداً للجامعة السويسرية لجراحة العظام في منطقة الشرق الأوسط وشمال أفريقيا."
            ),
            vision_ar="تقديم رعاية طبية متخصصة في جراحة العظام والمفاصل، تعتمد على الخبرة العلمية والتقنيات الجراحية الحديثة...",
            is_active=True
        )

        # 5 Official Qualifications
        official_educations = [
            ("أستاذ جراحة العظام", "كلية الطب، جامعة صنعاء"),
            ("دكتوراه في جراحة العظام", "جامعة القاهرة، مصر"),
            ("البورد العربي في جراحة العظام", "بيروت"),
            ("زمالة المفاصل الصناعية", "جامعة أسيوط، مصر"),
            ("زمالة المفاصل الصناعية باستخدام الروبوت", "الهند"),
        ]
        for idx, (deg, inst) in enumerate(official_educations, 1):
            Education.objects.create(
                doctor=self.doctor,
                degree_ar=deg,
                institution_ar=inst,
                degree_en=deg,
                institution_en=inst,
                year="",
                order=idx
            )

        # 5 Official Distinctions
        official_experiences = [
            "من أوائل الأطباء اليمنيين الحاصلين على شهادات في التخصص الدقيق للمفاصل الصناعية للركبة والحوض",
            "استشاري متخصص في كسور الحوض والمفاصل الصناعية",
            "زمالات تخصصية في جراحة المفاصل الصناعية من مصر والهند",
            "تدريب متخصص في تقنيات المفاصل الصناعية باستخدام الروبوت",
            "مدرب معتمد للجامعة السويسرية لجراحة العظام في الشرق الأوسط وشمال أفريقيا",
        ]
        for idx, text in enumerate(official_experiences, 1):
            Experience.objects.create(
                doctor=self.doctor,
                position_ar="خبرة متميزة",
                hospital_ar=text,
                position_en="Distinction",
                hospital_en=text,
                period_ar="تخصص رائد",
                period_en="Pioneering",
                order=idx
            )

        # 9 Official Services
        cat = ServiceCategory.objects.create(name_ar="جراحة العظام", name_en="Orthopedics", slug="ortho-cat")
        services_data = [
            ("جراحة العظام العامة", "general-orthopedic-surgery"),
            ("علاج الكسور وإصابات العظام بمختلف أنواعها", "fractures-and-bone-injuries"),
            ("جراحة كسور الحوض", "pelvic-fracture-surgery"),
            ("جراحة المفاصل الصناعية للركبة", "knee-joint-replacement"),
            ("جراحة المفاصل الصناعية للحوض", "hip-joint-replacement"),
            ("عمليات استبدال المفاصل الصناعية", "artificial-joint-replacement-surgeries"),
            ("جراحات المفاصل الصناعية باستخدام تقنيات الروبوت", "robotic-assisted-joint-replacement"),
            ("تقييم حالات خشونة وتآكل المفاصل", "assessment-osteoarthritis-joint-wear"),
            ("متابعة المرضى بعد عمليات استبدال المفاصل وإعادة التأهيل", "post-op-followup-and-rehabilitation"),
        ]
        for idx, (title, slug) in enumerate(services_data, 1):
            MedicalService.objects.create(
                category=cat,
                title_ar=title,
                title_en=title,
                slug=slug,
                short_desc_ar=f"وصف مختصر لـ {title}",
                short_desc_en=f"Short description for {title}",
                full_desc_ar=f"شرح تفصيلي معتمد لـ {title}",
                full_desc_en=f"Full description for {title}",
                order=idx,
                is_active=True
            )

    def test_homepage_official_information_and_no_placeholder_leak(self):
        response = self.client.get(reverse('public:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check official display name and title
        self.assertIn("الدكتور محمد الصياد", content)
        self.assertIn("استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية", content)

        # Check official address and phone
        self.assertIn("شارع خولان", content)
        self.assertIn("مركز الرازي الطبي", content)
        self.assertIn("783517733", content)
        self.assertIn('href="tel:783517733"', content)

        # Check vision statement
        self.assertIn("تقديم رعاية طبية متخصصة في جراحة العظام والمفاصل", content)

        # Verify old address is strictly absent
        self.assertNotIn("شارع الزبيري", content)
        self.assertNotIn("Al-Zubairi", content)

        # Verify placeholder stats are strictly absent
        self.assertNotIn("+16", content)
        self.assertNotIn("4200", content)
        self.assertNotIn("15000", content)

    def test_official_five_qualifications_page(self):
        response = self.client.get(reverse('public:qualifications'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Verify all 5 official qualifications are present
        self.assertIn("أستاذ جراحة العظام", content)
        self.assertIn("كلية الطب، جامعة صنعاء", content)
        self.assertIn("دكتوراه في جراحة العظام", content)
        self.assertIn("جامعة القاهرة، مصر", content)
        self.assertIn("البورد العربي في جراحة العظام", content)
        self.assertIn("بيروت", content)
        self.assertIn("زمالة المفاصل الصناعية", content)
        self.assertIn("جامعة أسيوط، مصر", content)
        self.assertIn("زمالة المفاصل الصناعية باستخدام الروبوت", content)
        self.assertIn("الهند", content)

    def test_official_nine_services_page_and_details(self):
        response = self.client.get(reverse('public:services'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Verify 9 services titles appear
        services_titles = [
            "جراحة العظام العامة",
            "علاج الكسور وإصابات العظام بمختلف أنواعها",
            "جراحة كسور الحوض",
            "جراحة المفاصل الصناعية للركبة",
            "جراحة المفاصل الصناعية للحوض",
            "عمليات استبدال المفاصل الصناعية",
            "جراحات المفاصل الصناعية باستخدام تقنيات الروبوت",
            "تقييم حالات خشونة وتآكل المفاصل",
            "متابعة المرضى بعد عمليات استبدال المفاصل وإعادة التأهيل",
        ]
        for title in services_titles:
            self.assertIn(title, content)

        # Test single service detail page
        detail_resp = self.client.get(reverse('public:service_detail', kwargs={'slug': 'robotic-assisted-joint-replacement'}))
        self.assertEqual(detail_resp.status_code, 200)
        detail_content = detail_resp.content.decode('utf-8')
        self.assertIn("جراحات المفاصل الصناعية باستخدام تقنيات الروبوت", detail_content)
        self.assertIn("حجز موعد", detail_content)

    def test_official_expertise_page_and_robotics(self):
        response = self.client.get(reverse('public:expertise'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Verify distinction points
        self.assertIn("من أوائل الأطباء اليمنيين", content)
        self.assertIn("الجامعة السويسرية لجراحة العظام", content)
        self.assertIn("تقنيات الروبوت", content)

    def test_official_contact_page(self):
        response = self.client.get(reverse('public:contact'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn("شارع خولان", content)
        self.assertIn("مركز الرازي الطبي", content)
        self.assertIn("بجوار مستشفى الثورة", content)
        self.assertIn("783517733", content)
        self.assertNotIn("شارع الزبيري", content)

    def test_doctor_biography_about_page(self):
        response = self.client.get(reverse('public:about'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn("الدكتور محمد الصياد", content)
        self.assertIn("استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية", content)
        self.assertIn("جامعة صنعاء", content)
        self.assertIn("السويسرية لجراحة العظام", content)
        self.assertNotIn("شارع الزبيري", content)
