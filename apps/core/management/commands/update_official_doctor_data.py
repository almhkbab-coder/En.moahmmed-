from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.core.models import SiteSettings
from apps.doctors.models import DoctorProfile, Education, Experience, Certificate
from apps.clinics.models import Clinic, ClinicBranch
from apps.services.models import MedicalService, ServiceCategory


class Command(BaseCommand):
    help = "Updates the database with official doctor and clinic profile data (Phase 4A)"

    def handle(self, *args, **options):
        self.stdout.write("Updating official data for Dr. Mohammed Al-Sayyad...")

        # 1. Update SiteSettings
        settings = SiteSettings.get_settings()
        settings.clinic_name_ar = "عيادة الصياد"
        settings.clinic_name_en = "Al-Sayyad Clinic"
        settings.doctor_name_ar = "الدكتور محمد الصياد"
        settings.doctor_name_en = "Dr. Mohammed Al-Sayyad"
        settings.title_ar = "استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية"
        settings.title_en = "Consultant in Orthopedic Surgery, Trauma, Pelvis & Artificial Joints"
        settings.specialty_ar = "جراحة العظام والمفاصل"
        settings.specialty_en = "Orthopedic & Joint Surgery"
        settings.phone = "783517733"
        settings.mobile = "783517733"
        settings.whatsapp = "+967783517733"
        settings.email = "info@alsayyad-clinic.ye"
        settings.google_maps_url = "https://maps.app.goo.gl/Af193GvkHNBb3f358"
        settings.address_ar = "صنعاء – شارع خولان – عمارة الحبيشي – بجوار مستشفى الثورة العام – عيادات الرازي"
        settings.address_en = "Sana'a - Khawlan St. - Al-Hubaishi Bldg. - Next to Al-Thawra Hospital - Al-Razi Specialized Clinics"
        settings.logo = "branding/clinic_logo.jpg"
        settings.favicon = "branding/clinic_logo.jpg"
        settings.meta_title_ar = "الدكتور محمد الصياد | عيادة الصياد - جراحة العظام والمفاصل - صنعاء"
        settings.meta_title_en = "Dr. Mohammed Al-Sayyad | Al-Sayyad Clinic - Orthopedic & Joint Surgery - Sanaa"
        settings.meta_description_ar = "الموقع الرسمي لعيادة الصياد - إشراف الدكتور محمد الصياد، استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية. عيادات الرازي، شارع خولان، صنعاء."
        settings.meta_description_en = "Official website of Al-Sayyad Clinic - Directed by Dr. Mohammed Al-Sayyad, Consultant Orthopedic, Trauma, Pelvis and Joint Replacement Surgeon. Al-Razi Clinics, Khawlan St., Sanaa."
        settings.save()
        self.stdout.write(self.style.SUCCESS("[OK] SiteSettings updated successfully."))

        # 2. Update Clinic & ClinicBranch
        clinic, _ = Clinic.objects.get_or_create(id=1, defaults={
            'name_ar': "عيادة الصياد",
            'name_en': "Al-Sayyad Clinic",
        })
        clinic.name_ar = "عيادة الصياد"
        clinic.name_en = "Al-Sayyad Clinic"
        clinic.save()

        branch = ClinicBranch.objects.filter(is_primary=True).first()
        if not branch:
            branch = ClinicBranch.objects.first()
        if not branch:
            branch = ClinicBranch.objects.create(clinic=clinic, name_ar="عيادات الرازي التخصصية - عيادة الصياد", is_primary=True)

        branch.name_ar = "عيادات الرازي التخصصية - عيادة الصياد"
        branch.name_en = "Al-Razi Specialized Clinics - Al-Sayyad Clinic"
        branch.city_ar = "صنعاء"
        branch.city_en = "Sana'a"
        branch.address_ar = "صنعاء – شارع خولان – عمارة الحبيشي – بجوار مستشفى الثورة العام – عيادات الرازي"
        branch.address_en = "Sana'a - Khawlan St. - Al-Hubaishi Bldg. - Next to Al-Thawra Hospital - Al-Razi Clinics"
        branch.phone = "783517733"
        branch.whatsapp = "+967783517733"
        branch.email = "info@alsayyad-clinic.ye"
        branch.save()
        self.stdout.write(self.style.SUCCESS("[OK] Clinic & Branch updated successfully."))

        # 3. Update DoctorProfile
        doctor = DoctorProfile.objects.first()
        if not doctor:
            doctor = DoctorProfile.objects.create(
                name_ar="الدكتور محمد الصياد",
                name_en="Dr. Mohammed Al-Sayyad",
            )

        doctor.name_ar = "الدكتور محمد الصياد"
        doctor.name_en = "Dr. Mohammed Al-Sayyad"
        doctor.title_ar = "استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية"
        doctor.title_en = "Consultant in Orthopedic Surgery, Trauma, Pelvis & Artificial Joints"
        doctor.specialty_ar = "استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية وأستاذ جراحة العظام بكلية الطب – جامعة صنعاء"
        doctor.specialty_en = "Consultant in Orthopedic Surgery, Trauma, Pelvis & Joint Replacement, Professor at Sana'a University"
        
        doctor.bio_ar = (
            "الدكتور محمد الصياد استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية، "
            "وأستاذ جراحة العظام بكلية الطب – جامعة صنعاء، يمتلك خلفية علمية وتخصصية متقدمة في مجال جراحة العظام، "
            "مع اهتمام خاص بجراحات استبدال المفاصل الصناعية للركبة والحوض، وتقنيات المفاصل الصناعية باستخدام الروبوت.\n\n"
            "حصل الدكتور محمد الصياد على مؤهلات علمية وتخصصية من عدد من المؤسسات والجامعات الطبية، "
            "واكتسب خبرات متقدمة في جراحة العظام وجراحات المفاصل الصناعية، من خلال الدراسات العليا والزمالات والتدريب التخصصي داخل وخارج اليمن.\n\n"
            "ويُعد من الأطباء اليمنيين الرواد في مجال التخصص الدقيق للمفاصل الصناعية، وخاصة مفاصل الركبة والحوض، "
            "ويسعى إلى توظيف أحدث التقنيات والأساليب الجراحية الحديثة لتقديم رعاية طبية متقدمة، والمساهمة في تحسين جودة حياة المرضى واستعادة قدرتهم على الحركة والنشاط.\n\n"
            "كما يعمل مدرباً معتمداً للجامعة السويسرية لجراحة العظام في منطقة الشرق الأوسط وشمال أفريقيا، "
            "ويساهم في نقل الخبرات والمعرفة الطبية المتخصصة وتطوير الممارسات الجراحية الحديثة."
        )

        doctor.bio_en = (
            "Dr. Mohammed Al-Sayyad is a Consultant Orthopedic, Trauma, Pelvis, and Artificial Joint Surgeon, "
            "and Professor of Orthopedic Surgery at the Faculty of Medicine - Sana'a University. He holds an advanced "
            "academic and clinical background in orthopedics, with specialized focus on knee and hip arthroplasty "
            "and robotic-assisted joint replacement techniques.\n\n"
            "He has earned postgraduate qualifications and fellowships from renowned medical institutions and universities, "
            "gaining extensive surgical expertise inside and outside Yemen.\n\n"
            "He is regarded as one of Yemen's pioneering surgeons in specialized joint replacement, dedicated to utilizing "
            "modern surgical technologies to relieve pain, restore mobility, and improve patients' quality of life.\n\n"
            "He also serves as a certified trainer for the Swiss Orthopaedics University in the MENA region, "
            "contributing to professional surgical education and modern orthopedics practice."
        )

        doctor.vision_ar = (
            "تقديم رعاية طبية متخصصة في جراحة العظام والمفاصل، تعتمد على الخبرة العلمية والتقنيات الجراحية الحديثة، "
            "بهدف تخفيف الألم، واستعادة الحركة، وتحسين جودة حياة المرضى، وفق أعلى معايير الممارسة الطبية."
        )
        doctor.vision_en = (
            "Providing specialized medical care in orthopedic and joint surgery, based on scientific expertise "
            "and modern surgical techniques, aiming to relieve pain, restore mobility, and improve patients' quality of life "
            "in accordance with the highest medical standards."
        )

        doctor.profile_photo = "doctors/profile/dr_mohammed_alsayyad.jpg"
        doctor.hero_photo = "doctors/hero/dr_mohammed_alsayyad_hero.jpg"
        doctor.save()
        self.stdout.write(self.style.SUCCESS("[OK] DoctorProfile updated successfully."))
        # 4. Update Academic Qualifications (Exactly 5)
        official_educations = [
            {
                "degree_ar": "أستاذ جراحة العظام",
                "degree_en": "Professor of Orthopedic Surgery",
                "institution_ar": "كلية الطب، جامعة صنعاء",
                "institution_en": "Faculty of Medicine, Sana'a University",
                "year": "",
                "order": 1
            },
            {
                "degree_ar": "دكتوراه في جراحة العظام",
                "degree_en": "Doctorate (Ph.D.) in Orthopedic Surgery",
                "institution_ar": "جامعة القاهرة، مصر",
                "institution_en": "Cairo University, Egypt",
                "year": "",
                "order": 2
            },
            {
                "degree_ar": "البورد العربي في جراحة العظام",
                "degree_en": "Arab Board in Orthopedic Surgery",
                "institution_ar": "بيروت",
                "institution_en": "Beirut",
                "year": "",
                "order": 3
            },
            {
                "degree_ar": "زمالة المفاصل الصناعية",
                "degree_en": "Fellowship in Artificial Joint Replacement",
                "institution_ar": "جامعة أسيوط، مصر",
                "institution_en": "Assiut University, Egypt",
                "year": "",
                "order": 4
            },
            {
                "degree_ar": "زمالة المفاصل الصناعية باستخدام الروبوت",
                "degree_en": "Fellowship in Robotic-Assisted Joint Replacement",
                "institution_ar": "الهند",
                "institution_en": "India",
                "year": "",
                "order": 5
            },
        ]

        # Remove old education records and insert official ones cleanly
        doctor.educations.all().delete()
        for edu_data in official_educations:
            Education.objects.create(doctor=doctor, **edu_data)
        self.stdout.write(self.style.SUCCESS("[OK] 5 Official Academic Qualifications updated."))

        # 5. Update Professional Experience and Distinction (Official Points)
        official_experiences = [
            {
                "position_ar": "التخصص الدقيق في المفاصل الصناعية للركبة والحوض",
                "position_en": "Subspecialty in Knee and Hip Arthroplasty",
                "hospital_ar": "من أوائل الأطباء اليمنيين الحاصلين على شهادات في التخصص الدقيق للمفاصل الصناعية للركبة والحوض",
                "hospital_en": "One of the first Yemeni surgeons certified in knee and hip arthroplasty subspecialty",
                "period_ar": "خبرة تخصصية رائدة",
                "period_en": "Pioneering Subspecialty",
                "order": 1
            },
            {
                "position_ar": "استشاري متخصص في كسور الحوض والمفاصل الصناعية",
                "position_en": "Consultant in Pelvic Fractures & Joint Replacement",
                "hospital_ar": "إدارة وعلاج جراحي دقيق لحالات كسور الحوض المعقدة وتبديل المفاصل الصناعية",
                "hospital_en": "Expert management of complex pelvic trauma and total joint replacements",
                "period_ar": "ممارسة سريرية استشارية",
                "period_en": "Consultant Practice",
                "order": 2
            },
            {
                "position_ar": "زمالات تخصصية في جراحة المفاصل الصناعية",
                "position_en": "International Arthroplasty Fellowships",
                "hospital_ar": "زمالات تخصصية في جراحة المفاصل الصناعية من مصر والهند",
                "hospital_en": "Specialized Arthroplasty Fellowships from Egypt and India",
                "period_ar": "تدريب سريري دولي",
                "period_en": "International Training",
                "order": 3
            },
            {
                "position_ar": "تدريب متخصص في تقنيات المفاصل الصناعية باستخدام الروبوت",
                "position_en": "Robotic-Assisted Joint Replacement Training",
                "hospital_ar": "توظيف أحدث التقنيات التكنولوجية والجراحية الروبوتية في زراعة المفاصل",
                "hospital_en": "Application of modern robotic navigation technologies in joint surgery",
                "period_ar": "تقنيات جراحية حديثة",
                "period_en": "Advanced Technology",
                "order": 4
            },
            {
                "position_ar": "مدرب معتمد للجامعة السويسرية لجراحة العظام",
                "position_en": "Certified Trainer - Swiss Orthopaedics University",
                "hospital_ar": "مدرب معتمد للجامعة السويسرية لجراحة العظام في الشرق الأوسط وشمال أفريقيا",
                "hospital_en": "Certified Trainer for Swiss Orthopaedics University in MENA Region",
                "period_ar": "تدريب وتطوير جراحي",
                "period_en": "Regional Trainer",
                "order": 5
            },
        ]

        doctor.experiences.all().delete()
        for exp_data in official_experiences:
            Experience.objects.create(doctor=doctor, **exp_data)
        self.stdout.write(self.style.SUCCESS("[OK] 5 Official Professional Experience records updated."))

        # 6. Update Medical Specialties and Services (Exactly 9 Services)
        general_cat, _ = ServiceCategory.objects.get_or_create(
            slug="orthopedic-services",
            defaults={"name_ar": "خدمات وجراحات العظام والمفاصل", "name_en": "Orthopedic & Joint Services", "order": 1}
        )

        official_services = [
            {
                "title_ar": "جراحة العظام العامة",
                "title_en": "General Orthopedic Surgery",
                "slug": "general-orthopedic-surgery",
                "short_desc_ar": "تشخيص وعلاج أمراض وتشوهات الجهاز العضلي الهيكلي والعظام والمفاصل وفق أعلى المعايير الطبية المعتمدة.",
                "short_desc_en": "Diagnosis and surgical management of musculoskeletal conditions and bone disorders.",
                "full_desc_ar": "تشمل جراحة العظام العامة التقييم الطبي الدقيق والعلاج الجراحي والتحفظي لمختلف أمراض وتشوهات الهيكل العظمي والمفاصل، بالاعتماد على أسس سريرية حديثة تهدف إلى استعادة الحركة وتخفيف الألم وتحسين وظيفة الجهاز الحركي للمريض.",
                "full_desc_en": "General orthopedic surgery encompasses thorough clinical evaluation and treatment of various skeletal and joint disorders based on established medical practices.",
                "icon": "bi-hospital",
                "featured_image": "services/general_orthopedics.jpg",
                "is_featured": True,
                "order": 1,
            },
            {
                "title_ar": "علاج الكسور وإصابات العظام بمختلف أنواعها",
                "title_en": "Treatment of Fractures and Bone Injuries",
                "slug": "fractures-and-bone-injuries",
                "short_desc_ar": "علاج وتثبيت مختلف أنواع الكسور البسيطة والمعقدة وإصابات العظام لضمان التئام سليم واستعادة وظيفة الطرف المصاب.",
                "short_desc_en": "Comprehensive treatment and fixation of simple and complex fractures and bone trauma.",
                "full_desc_ar": "تقديم الرعاية المتخصصة في التعامل مع مختلف أنواع كسور العظام والإصابات الحادة، باستخدام تقنيات التثبيت الداخلي والخارجي الحديثة التي تعزز الالتئام السريع للعظام وتقلل من احتمالية حدوث مضاعفات أو تشوهات لاحقة.",
                "full_desc_en": "Specialized care for various fracture patterns and bone trauma utilizing modern internal and external fixation techniques for optimal bone healing.",
                "icon": "bi-bandaid",
                "is_featured": True,
                "order": 2,
            },
            {
                "title_ar": "جراحة كسور الحوض",
                "title_en": "Pelvic Fracture Surgery",
                "slug": "pelvic-fracture-surgery",
                "short_desc_ar": "علاج جراحي دقيق ومتخصص لكسور وتفككات الحوض المعقدة بالاعتماد على خبرة استشارية جراحية متقدمة.",
                "short_desc_en": "Advanced surgical management of complex pelvic ring fractures and acetabular trauma.",
                "full_desc_ar": "تعد جراحة كسور الحوض من أدق التخصصات في جراحة الكسور، وتتطلب مهارة جراحية استشارية عالية لإعادة بناء وتثبيت عظام الحوض والحق بدقة متناهية للحفاظ على استقرار المفصل واستعادة قدرة المريض على الوقوف والحركة.",
                "full_desc_en": "Pelvic and acetabular surgery requires advanced surgical expertise to reconstruct and stabilize complex pelvic injuries, restoring anatomical integrity and patient mobility.",
                "icon": "bi-shield-plus",
                "is_featured": True,
                "order": 3,
            },
            {
                "title_ar": "جراحة المفاصل الصناعية للركبة",
                "title_en": "Knee Arthroplasty (Joint Replacement)",
                "slug": "knee-joint-replacement",
                "short_desc_ar": "استبدال مفصل الركبة التالف بمفصل صناعي متطور لتخفيف الآلام المزمنة وتحسين القدرة على المشي والحركة الطبيعية.",
                "short_desc_en": "Total and partial knee arthroplasty to relieve chronic pain and restore joint function.",
                "full_desc_ar": "إجراء عمليات استبدال مفصل الركبة الكلي والجزئي للمرضى الذين يعانون من تآكل متقدم أو احتكاك شديد لا يستجيب للعلاجات التحفظية، باستخدام مفاصل صناعية عالية الجودة وتقنيات جراحية تحافظ على الأنسجة المحيطة بالمفصل.",
                "full_desc_en": "Total and partial knee replacement procedures for severe joint wear, employing high-quality prosthetic components and tissue-preserving surgical methods.",
                "icon": "bi-activity",
                "is_featured": True,
                "order": 4,
            },
            {
                "title_ar": "جراحة المفاصل الصناعية للحوض",
                "title_en": "Hip Arthroplasty (Joint Replacement)",
                "slug": "hip-joint-replacement",
                "short_desc_ar": "عمليات استبدال مفصل الورك والحوض باستخدام أحدث أنواع المفاصل الصناعية لاستعادة استقرار المفصل ومدى حركته.",
                "short_desc_en": "Total hip replacement utilizing advanced prosthetic designs for stability and mobility.",
                "full_desc_ar": "استبدال مفصل الورك التالف لعلاج حالات الخشونة المتقدمة، نخر رأس الفخذ، أو الكسور، عبر تركيب مفاصل صناعية ملائمة تشريحياً تساعد المريض على التخلص من الآلام واستئناف نشاطه اليومي بأمان.",
                "full_desc_en": "Hip replacement surgery for advanced osteoarthritis, avascular necrosis, or fractures, providing pain relief and joint stability.",
                "icon": "bi-heart-pulse",
                "is_featured": True,
                "order": 5,
            },
            {
                "title_ar": "عمليات استبدال المفاصل الصناعية",
                "title_en": "Artificial Joint Replacement Surgeries",
                "slug": "artificial-joint-replacement-surgeries",
                "short_desc_ar": "إجراء عمليات استبدال المفاصل الأولية والمراجعة وفق خطة جراحية فردية ملائمة لكل حالة سريرية.",
                "short_desc_en": "Comprehensive primary and revision artificial joint replacement surgical care.",
                "full_desc_ar": "منظومة متكاملة لعمليات المفاصل الصناعية تشمل التقييم ما قبل الجراحة، والتخطيط الجراحي الدقيق، والعمليات الأولية وعمليات المراجعة، وفق بروتوكولات تعقيم ومعايير جراحية دقيقة لضمان أعلى نسب الأمان والنجاح.",
                "full_desc_en": "A complete surgical framework for primary and revision joint arthroplasty, emphasizing thorough preoperative planning and strict sterile protocols.",
                "icon": "bi-gear-wide-connected",
                "is_featured": True,
                "order": 6,
            },
            {
                "title_ar": "جراحات المفاصل الصناعية باستخدام تقنيات الروبوت",
                "title_en": "Robotic-Assisted Joint Replacement Surgeries",
                "slug": "robotic-assisted-joint-replacement",
                "short_desc_ar": "توظيف تقنيات الملاحة الجراحية والروبوت المتقدمة لتحقيق أعلى درجات الدقة في موازنة وتركيب المفصل الصناعي.",
                "short_desc_en": "Utilization of advanced surgical navigation and robotic technology for precise joint implant positioning.",
                "full_desc_ar": "تعتمد جراحة المفاصل المدعومة بالروبوت على التخطيط الرقمي ثلاثي الأبعاد والتوجيه الحركي الملاحي أثناء العملية، مما يساعد الجراح في قطع العظم وموازنة الأربطة بدقة عالية ترفع من كفاءة وثبات المفصل الصناعي وطول عمره الافتراضي.",
                "full_desc_en": "Robotic-assisted joint surgery combines 3D preoperative planning with real-time navigation to achieve optimal bone cuts, implant alignment, and soft-tissue balance.",
                "icon": "bi-cpu",
                "is_featured": True,
                "order": 7,
            },
            {
                "title_ar": "تقييم حالات خشونة وتآكل المفاصل",
                "title_en": "Assessment of Osteoarthritis and Joint Wear",
                "slug": "assessment-osteoarthritis-joint-wear",
                "short_desc_ar": "تقييم سريري وإشعاعي شامل لدرجات احتكاك وخشونة المفاصل واقتراح الخطة العلاجية والتحفظية الأنسب.",
                "short_desc_en": "Comprehensive clinical and radiological evaluation of joint wear and osteoarthritis progression.",
                "full_desc_ar": "فحص طبي وسريري دقيق لمرضى آلام المفاصل والخشونة، يشمل مراجعة الصور الشعاعية والرنين المغناطيسي، وتقديم استشارة طبية موضوعية تشمل خيارات العلاج التحفظي والدوائي وتحديد التوقيت الطبي المناسب للتدخل الجراحي عند الحاجة.",
                "full_desc_en": "Detailed assessment of joint wear through clinical examination and imaging, guiding conservative management and timing of surgical intervention when indicated.",
                "icon": "bi-clipboard2-pulse",
                "is_featured": False,
                "order": 8,
            },
            {
                "title_ar": "متابعة المرضى بعد عمليات استبدال المفاصل وإعادة التأهيل",
                "title_en": "Post-Operative Follow-up and Joint Rehabilitation",
                "slug": "post-op-followup-and-rehabilitation",
                "short_desc_ar": "برامج متابعة دورية دقيقة بعد الجراحة لتقييم المفصل والإشراف على إعادة التأهيل الحركي لتحقيق أفضل النتائج.",
                "short_desc_en": "Structured post-operative follow-up programs and functional rehabilitation monitoring.",
                "full_desc_ar": "برنامج رعاية ومتابعة مستمر يبدأ بعد إجراء الجراحة، يركز على سلامة الجرح، والتأكد من استقرار المفصل، ووضع توجيهات العلاج الطبيعي والتأهيل الحركي بالتعاون مع فرق العلاج الطبيعي لضمان عودة المريض لممارسة حياته بثقة.",
                "full_desc_en": "Structured clinical follow-up ensuring wound healing, implant stability, and proper physical rehabilitation guidance for complete functional recovery.",
                "icon": "bi-person-walking",
                "is_featured": False,
                "order": 9,
            },
        ]

        # Update or create the 9 services
        for s_data in official_services:
            slug = s_data['slug']
            service, created = MedicalService.objects.get_or_create(
                slug=slug,
                defaults={**s_data, 'category': general_cat}
            )
            if not created:
                for key, val in s_data.items():
                    setattr(service, key, val)
                service.category = general_cat
                service.is_active = True
                service.save()

        # Disable any old services that don't match the official 9
        official_slugs = [s['slug'] for s in official_services]
        MedicalService.objects.exclude(slug__in=official_slugs).update(is_active=False, is_featured=False)
        self.stdout.write(self.style.SUCCESS("[OK] 9 Official Medical Services created/updated and activated."))

        self.stdout.write(self.style.SUCCESS("All official data successfully synchronized!"))
