import os
import secrets
from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group, Permission

from apps.accounts.models import CustomUser
from apps.core.models import SiteSettings, ActivityLog
from apps.doctors.models import DoctorProfile, Education, Experience, Certificate
from apps.clinics.models import Clinic, ClinicBranch, WorkingHours, ClinicHoliday
from apps.services.models import ServiceCategory, MedicalService
from apps.education.models import EducationalSeries, EducationalVideo
from apps.blog.models import ArticleCategory, ArticleTag, Article
from apps.appointments.models import Patient, Appointment, AppointmentStatusHistory


class Command(BaseCommand):
    help = 'Seeds realistic initial medical data for Dr. Mohammed Ahmed Al-Sayyad Clinic'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting clinic data seeding...'))

        # 1. Setup Groups & Roles
        admin_group, _ = Group.objects.get_or_create(name='Super Administrator')
        doctor_group, _ = Group.objects.get_or_create(name='Doctor')
        receptionist_group, _ = Group.objects.get_or_create(name='Receptionist')
        content_group, _ = Group.objects.get_or_create(name='Content Manager')

        # 2. Setup Superuser & Staff Accounts with Secure Credentials
        admin_pw = os.environ.get('ADMIN_INITIAL_PASSWORD')
        admin_generated = False
        if not admin_pw:
            admin_pw = secrets.token_urlsafe(14)
            admin_generated = True

        if not CustomUser.objects.filter(username='admin').exists():
            admin_user = CustomUser.objects.create_superuser(
                username='admin',
                email='admin@alsayyad-clinic.ye',
                password=admin_pw,
                first_name='المدير',
                last_name='العام',
                phone_number='+967 777 000 000',
                role=CustomUser.Role.SUPER_ADMIN
            )
            admin_user.groups.add(admin_group)
            if admin_generated:
                self.stdout.write(self.style.WARNING(f'[SECURITY] Generated secure superuser password: {admin_pw} (Please save and change on first login)'))
            else:
                self.stdout.write(self.style.SUCCESS('Created superuser from environment password.'))
        else:
            admin_user = CustomUser.objects.get(username='admin')

        # Create Receptionist user
        reception_pw = os.environ.get('RECEPTION_INITIAL_PASSWORD')
        reception_generated = False
        if not reception_pw:
            reception_pw = secrets.token_urlsafe(14)
            reception_generated = True

        if not CustomUser.objects.filter(username='reception').exists():
            reception_user = CustomUser.objects.create_user(
                username='reception',
                email='reception@alsayyad-clinic.ye',
                password=reception_pw,
                first_name='موظف',
                last_name='الاستقبال',
                phone_number='+967 777 111 222',
                role=CustomUser.Role.RECEPTIONIST,
                is_staff=True
            )
            reception_user.groups.add(receptionist_group)
            if reception_generated:
                self.stdout.write(self.style.WARNING(f'[SECURITY] Generated secure receptionist password: {reception_pw} (Please save and change on first login)'))
            else:
                self.stdout.write(self.style.SUCCESS('Created receptionist from environment password.'))

        # 3. Global Site Settings
        settings_obj = SiteSettings.get_settings()
        settings_obj.clinic_name_ar = 'عيادة الدكتور محمد الصياد'
        settings_obj.clinic_name_en = 'Dr. Mohammed Al-Sayyad Clinic'
        settings_obj.doctor_name_ar = 'الدكتور محمد أحمد الصياد'
        settings_obj.doctor_name_en = 'Dr. Mohammed Ahmed Al-Sayyad'
        settings_obj.specialty_ar = 'استشاري جراحة العظام والمفاصل الصناعية'
        settings_obj.specialty_en = 'Consultant Orthopedic & Joint Replacement Surgeon'
        settings_obj.phone = '+967 1 205600'
        settings_obj.mobile = '+967 777 345 678'
        settings_obj.whatsapp = '+967 777 345 678'
        settings_obj.email = 'contact@alsayyad-clinic.ye'
        settings_obj.address_ar = 'صنعاء - شارع الزبيري - برج النخبة الطبي - الدور الثالث'
        settings_obj.address_en = "Sana'a - Al-Zubairi St. - Al-Nukhba Medical Tower - 3rd Floor"
        settings_obj.working_hours_summary_ar = 'السبت - الخميس: 9:00 ص - 1:00 م | 4:00 م - 8:30 م (الجمعة عطلة)'
        settings_obj.working_hours_summary_en = 'Sat - Thu: 9:00 AM - 1:00 PM | 4:00 PM - 8:30 PM (Friday Closed)'
        settings_obj.save()

        # 4. Clinic & Branch
        clinic, _ = Clinic.objects.get_or_create(
            name_ar='عيادة الدكتور محمد الصياد',
            defaults={
                'name_en': 'Dr. Mohammed Al-Sayyad Clinic',
                'description_ar': 'عيادة تخصصية رائدة في صنعاء تقدم أحدث الحلول الجراحية الدقيقة لتبديل مفاصل الركبة والورك وعلاج خشونة المفاصل والكسور المعقدة.',
                'description_en': 'Premier orthopedic clinic in Sanaa providing cutting-edge joint replacement and musculoskeletal care.'
            }
        )

        branch, _ = ClinicBranch.objects.get_or_create(
            clinic=clinic,
            name_ar='الفرع الرئيسي - صنعاء',
            defaults={
                'name_en': 'Main Clinic - Sanaa',
                'city_ar': 'صنعاء',
                'city_en': "Sana'a",
                'address_ar': 'صنعاء - شارع الزبيري - برج النخبة الطبي - الدور الثالث',
                'address_en': "Sana'a - Al-Zubairi St. - Al-Nukhba Medical Tower",
                'phone': '+967 1 205600',
                'whatsapp': '+967 777 345 678',
                'email': 'sanaa@alsayyad-clinic.ye',
                'is_primary': True,
                'is_active': True,
                'latitude': 15.354722,
                'longitude': 44.206667
            }
        )

        # 5. Working Hours (Saturday to Thursday: 09:00-13:00 and 16:00-20:30, Friday closed)
        for day_code in range(7):
            is_friday = (day_code == 6)
            WorkingHours.objects.update_or_create(
                branch=branch,
                day_of_week=day_code,
                defaults={
                    'morning_start': None if is_friday else time(9, 0),
                    'morning_end': None if is_friday else time(13, 0),
                    'evening_start': None if is_friday else time(16, 0),
                    'evening_end': None if is_friday else time(20, 30),
                    'slot_duration_minutes': 20,
                    'is_closed': is_friday
                }
            )

        # 6. Doctor Profile & Qualifications
        doc_profile, _ = DoctorProfile.objects.get_or_create(
            id=1,
            defaults={
                'user': admin_user,
                'name_ar': 'الدكتور محمد أحمد الصياد',
                'name_en': 'Dr. Mohammed Ahmed Al-Sayyad',
                'title_ar': 'استشاري أول جراحة العظام والمفاصل الصناعية',
                'title_en': 'Senior Consultant in Orthopedic & Joint Replacement Surgery',
                'specialty_ar': 'جراحة المفاصل الصناعية وتبديل الركبة والورك وتنظير المفاصل وعلاج الكسور المعقدة',
                'specialty_en': 'Total Knee & Hip Arthroplasty, Arthroscopy, and Complex Trauma Surgery',
                'years_of_experience': 16,
                'successful_surgeries': 4200,
                'consultations_count': 15000,
                'is_active': True
            }
        )

        # Add Qualifications
        Education.objects.get_or_create(
            doctor=doc_profile,
            degree_ar='البورد التخصصي في جراحة العظام والمفاصل',
            defaults={
                'degree_en': 'Specialty Board in Orthopedic & Joint Surgery',
                'institution_ar': 'المجلس العربي للاختصاصات الصحية',
                'institution_en': 'Arab Board of Health Specializations',
                'year': '2012',
                'order': 1
            }
        )
        Education.objects.get_or_create(
            doctor=doc_profile,
            degree_ar='زمالة جراحة المفاصل الصناعية المتقدمة وتبديل الركبة والورك',
            defaults={
                'degree_en': 'Fellowship in Advanced Arthroplasty & Joint Replacement',
                'institution_ar': 'مراكز جراحة العظام التخصصية',
                'institution_en': 'Specialized Arthroplasty Center',
                'year': '2015',
                'order': 2
            }
        )
        Education.objects.get_or_create(
            doctor=doc_profile,
            degree_ar='بكالوريوس الطب العام والجراحة (MBBS)',
            defaults={
                'degree_en': 'Bachelor of Medicine and Surgery (MBBS)',
                'institution_ar': 'جامعة صنعاء - كلية الطب والعلوم الصحية',
                'institution_en': "Sana'a University - Faculty of Medicine",
                'year': '2006',
                'order': 3
            }
        )

        # Add Clinical Experience
        Experience.objects.get_or_create(
            doctor=doc_profile,
            position_ar='استشاري جراحة العظام والمفاصل ورئيس وحدة المفاصل الصناعية',
            defaults={
                'position_en': 'Consultant Orthopedic Surgeon & Head of Arthroplasty Unit',
                'hospital_ar': 'المستشفيات التخصصية التعليمية - صنعاء',
                'hospital_en': "Specialized Teaching Hospitals - Sana'a",
                'period_ar': '2016 - حتى الآن',
                'period_en': '2016 - Present',
                'order': 1
            }
        )
        Experience.objects.get_or_create(
            doctor=doc_profile,
            position_ar='أخصائي جراحة العظام والإصابات والحوادث',
            defaults={
                'position_en': 'Orthopedic Trauma Specialist',
                'hospital_ar': 'مستشفى الثورة العام النموذجي - صنعاء',
                'hospital_en': "Al-Thawra General Hospital - Sana'a",
                'period_ar': '2012 - 2016',
                'period_en': '2012 - 2016',
                'order': 2
            }
        )

        # 7. Medical Services Categories & Services
        cat_joints, _ = ServiceCategory.objects.get_or_create(
            slug='joint-replacement',
            defaults={'name_ar': 'جراحة المفاصل الصناعية', 'name_en': 'Joint Replacement', 'icon': 'bi-gear-wide-connected', 'order': 1}
        )
        cat_arthroscopy, _ = ServiceCategory.objects.get_or_create(
            slug='arthroscopy-sports',
            defaults={'name_ar': 'تنظير المفاصل والإصابات الرياضية', 'name_en': 'Arthroscopy & Sports Injuries', 'icon': 'bi-activity', 'order': 2}
        )
        cat_trauma, _ = ServiceCategory.objects.get_or_create(
            slug='trauma-fractures',
            defaults={'name_ar': 'جراحة الكسور المعقدة وتشوهات العظام', 'name_en': 'Complex Trauma & Deformities', 'icon': 'bi-bandaid', 'order': 3}
        )

        services_data = [
            {
                'category': cat_joints,
                'title_ar': 'عملية استبدال مفصل الركبة الصناعي (Total Knee Arthroplasty)',
                'title_en': 'Total Knee Replacement Surgery',
                'slug': 'total-knee-replacement',
                'short_desc_ar': 'استبدال أسطح مفصل الركبة المتآكلة بمفصل صناعي متطور لاستعادة الحركة والتخلص النهائي من الآلام المزمنة.',
                'short_desc_en': 'Replacing damaged joint surfaces with advanced prosthetics to restore pain-free walking and full mobility.',
                'full_desc_ar': 'تعد عملية تبديل مفصل الركبة من أنجح العمليات الجراحية عالمياً لعلاج الخشونة المتقدمة وتآكل الغضاريف. نستخدم في عيادة الدكتور محمد الصياد تقنيات جراحية دقيقة لتقليل فقدان الدم، مع مفاصل معتمدة طبياً تدوم لسنوات طويلة، وبرنامج تأهيلي يبدأ من اليوم الأول بعد العملية لضمان سرعة عودة المريض لحياته الطبيعية.',
                'full_desc_en': 'Total knee replacement is one of the most successful surgical procedures for advanced osteoarthritis. We employ minimally invasive techniques with high-grade implants and immediate postoperative rehabilitation.',
                'icon': 'bi-check2-circle',
                'is_featured': True,
                'order': 1
            },
            {
                'category': cat_joints,
                'title_ar': 'عملية استبدال مفصل الورك الصناعي (Total Hip Replacement)',
                'title_en': 'Total Hip Replacement Surgery',
                'slug': 'total-hip-replacement',
                'short_desc_ar': 'علاج متكامل لتنكس وتآكل رأس عظم الفخذ ومفصل الحوض واستعادة القدرة على المشي الطبيعي.',
                'short_desc_en': 'Comprehensive surgical solution for hip osteoarthritis and avascular necrosis to regain painless movement.',
                'full_desc_ar': 'عملية استبدال مفصل الورك تهدف إلى استئصال المفصل المتضرر وزراعة مفصل صناعي متطابق مع التشريح الحركي للمريض، مما يزيل آلام الورك تماماً ويعيد التوازن الحركي وجودة الحياة.',
                'full_desc_en': 'Hip arthroplasty replaces the damaged joint components with biocompatible implants, completely eliminating chronic hip pain and restoring mobility.',
                'icon': 'bi-shield-check',
                'is_featured': True,
                'order': 2
            },
            {
                'category': cat_arthroscopy,
                'title_ar': 'تنظير مفصل الركبة وإصلاح الغضاريف الهلالية (Knee Arthroscopy)',
                'title_en': 'Knee Arthroscopy & Meniscal Repair',
                'slug': 'knee-arthroscopy',
                'short_desc_ar': 'جراحة اليوم الواحد الدقيقة عبر ثقوب صغيرة لتشخيص وعلاج تمزق الغضاريف والأربطة بالمنظار الطبي.',
                'short_desc_en': 'Minimally invasive keyhole surgery to repair torn menisci and cartilage with rapid recovery time.',
                'full_desc_ar': 'يتميز التنظير الجراحي للركبة بكونه إجراءً دقيقاً يتم من خلال فتحات مليمترية صغيرة، مما يقلل الألم ويسرع الشفاء. نقوم بإصلاح الغضاريف الهلالية المتمزقة واستئصال الزوائد العظمية ومعالجة التهابات الغشاء السينوفي.',
                'full_desc_en': 'Arthroscopy allows direct visualization and repair of intra-articular structures through tiny incisions, offering faster healing and minimal discomfort.',
                'icon': 'bi-eye',
                'is_featured': True,
                'order': 3
            },
            {
                'category': cat_arthroscopy,
                'title_ar': 'إعادة بناء الرباط الصليبي الأمامي (ACL Reconstruction)',
                'title_en': 'Anterior Cruciate Ligament (ACL) Reconstruction',
                'slug': 'acl-reconstruction',
                'short_desc_ar': 'ترميم الرباط الصليبي بالمنظار للرياضيين والمرضى لاستعادة ثبات الركبة ومنع التآكل المستقبلي.',
                'short_desc_en': 'Arthroscopic reconstruction of torn ACL to restore knee stability and allow safe return to sports.',
                'full_desc_ar': 'جراحة إعادة بناء الرباط الصليبي بتقنيات التطعيم الذاتي للأوتار وتثبيتها بوسائل متطورة، يتبعها برنامج علاج طبيعي متخصص لإعادة الرياضيين إلى كامل لياقتهم.',
                'full_desc_en': 'Autograft reconstruction of the ACL using modern anatomical fixation devices, combined with structured rehabilitation for athletic recovery.',
                'icon': 'bi-lightning-charge',
                'is_featured': True,
                'order': 4
            },
            {
                'category': cat_trauma,
                'title_ar': 'جراحة الكسور المعقدة وإصابات الحوادث (Complex Trauma Surgery)',
                'title_en': 'Complex Trauma & Fracture Fixation',
                'slug': 'complex-fracture-surgery',
                'short_desc_ar': 'تثبيت كسور العظام المتفتتة والمفاصل باستخدام الشرائح الدقيقة والمسامير التيتانيوم والمثبتات الخارجية.',
                'short_desc_en': 'Internal and external fixation of complex intra-articular fractures using titanium plates and rods.',
                'full_desc_ar': 'خبرة واسعة في تدبير وعلاج الكسور المتفتتة المعقدة حول المفاصل، وعلاج حالات عدم التئام الكسور أو الالتئام المعيب، مع الحفاظ على التروية الدموية للأنسجة المحيطة.',
                'full_desc_en': 'Expert management of complex peri-articular fractures, non-unions, and malunions with anatomical restoration and tissue preservation.',
                'icon': 'bi-tools',
                'is_featured': True,
                'order': 5
            },
            {
                'category': cat_trauma,
                'title_ar': 'علاج خشونة والتهابات المفاصل بدون جراحة (Joint Injections & Therapies)',
                'title_en': 'Non-Surgical Joint Therapies & Injections',
                'slug': 'non-surgical-joint-therapies',
                'short_desc_ar': 'حقن البلازما الغنية بالصفائح (PRP) وحمض الهيالورونيك الزيتي لتهدئة الخشونة وتغذية الغضروف.',
                'short_desc_en': 'PRP and hyaluronic acid visco-supplementation injections to manage early to moderate joint degeneration.',
                'full_desc_ar': 'بروتوكولات علاجية تحفظية متطورة لتخفيف آلام المفاصل وتأخير الحاجة للتدخل الجراحي من خلال الحقن المفصلية الدقيقة وبرامج تقوية العضلات المحيطة بالمفصل.',
                'full_desc_en': 'Conservative regenerative therapies designed to reduce joint inflammation, lubricate cartilage, and postpone surgical intervention.',
                'icon': 'bi-droplet-half',
                'is_featured': True,
                'order': 6
            }
        ]

        for s_data in services_data:
            MedicalService.objects.update_or_create(
                slug=s_data['slug'],
                defaults=s_data
            )

        # 8. Educational Series & Videos (Real YouTube content IDs)
        series_joints, _ = EducationalSeries.objects.get_or_create(
            slug='knee-joint-care-series',
            defaults={
                'title_ar': 'سلسلة التوعية بصحة مفاصل الركبة والمفاصل الصناعية',
                'title_en': 'Knee Joint Health & Arthroplasty Series',
                'description_ar': 'سلسلة طبية شاملة يشرح فيها الدكتور محمد الصياد كل ما يتعلق بأمراض المفاصل، درجات الخشونة، متى يتقرر استبدال المفصل، وكيفية التأهيل السليم.',
                'description_en': 'A comprehensive educational guide by Dr. Mohammed Al-Sayyad covering joint degeneration, surgical indicators, and rehabilitation.',
                'is_published': True,
                'order': 1
            }
        )

        videos_data = [
            {
                'series': series_joints,
                'title_ar': 'متى تصبح عملية تبديل مفصل الركبة ضرورية؟ درجات الخشونة والعلامات',
                'title_en': 'When is Total Knee Replacement Necessary?',
                'slug': 'when-knee-replacement-needed',
                'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'duration_minutes': 7,
                'episode_number': 1,
                'description_ar': 'شرح مفصل لدرجات تآكل غضروف الركبة من الدرجة الأولى حتى الرابعة، والأعراض التي تشير إلى أن الجراحة هي الخيار الأنسب للمريض.'
            },
            {
                'series': series_joints,
                'title_ar': 'نصائح ما بعد عملية المفصل الصناعي: متى يمشي المريض وما هي المحاذير؟',
                'title_en': 'Post-Op Knee Replacement Care & Milestones',
                'slug': 'post-op-knee-replacement-tips',
                'youtube_url': 'https://www.youtube.com/watch?v=kJQP7kiw5Fk',
                'duration_minutes': 8,
                'episode_number': 2,
                'description_ar': 'خطوات المشي بعد العملية، تمارين تقوية العضلة الرباعية، والعناية بالجرح لمنع أي مضاعفات وضمان الشفاء التام.'
            },
            {
                'series': series_joints,
                'title_ar': 'حقن الركبة بالبلازما والزيت: متى تفيد ومتى لا تكون كافية؟',
                'title_en': 'Joint Injections: PRP vs Hyaluronic Acid',
                'slug': 'joint-injections-prp-hyaluronic',
                'youtube_url': 'https://www.youtube.com/watch?v=3JZ_D3ELwOQ',
                'duration_minutes': 6,
                'episode_number': 3,
                'description_ar': 'توضيح علمي حول الفروق بين حقن البلازما وحقن الزيت، والمرضى المؤهلين للاستفادة منها بدون جراحة.'
            }
        ]

        for v_data in videos_data:
            EducationalVideo.objects.update_or_create(
                slug=v_data['slug'],
                defaults=v_data
            )

        # 9. Medical Articles & Blog
        blog_cat_joints, _ = ArticleCategory.objects.get_or_create(
            slug='joint-health',
            defaults={'name_ar': 'صحة المفاصل والعظام', 'name_en': 'Joint & Bone Health'}
        )
        blog_cat_recovery, _ = ArticleCategory.objects.get_or_create(
            slug='rehabilitation-recovery',
            defaults={'name_ar': 'التأهيل والتعافي الطبي', 'name_en': 'Rehabilitation & Recovery'}
        )

        articles_data = [
            {
                'category': blog_cat_joints,
                'title_ar': 'دليلك الشامل لعملية استبدال مفصل الركبة الصناعي: التقنيات والنتائج',
                'title_en': 'Complete Guide to Total Knee Arthroplasty',
                'slug': 'guide-to-knee-replacement',
                'excerpt_ar': 'كل ما يحتاج المريض لمعرفته قبل الخضوع لعملية تبديل المفصل: خطوات الإجراء، أنواع المفاصل الصناعية، ونسبة نجاح العملية العالية.',
                'excerpt_en': 'Everything patients need to understand before undergoing joint replacement surgery.',
                'content_ar': '''يعاني ملايين الأشخاص حول العالم من خشونة مفصل الركبة المتقدمة التي تجعل مجرد المشي أو صعود الدرج تجربة مؤلمة للغاية. عندما تفشل العلاجات الدوائية والتمارين الرياضية في تخفيف الألم، تصبح عملية استبدال مفصل الركبة الخيار الطبي الذهبي لاستعادة الحركة الحرة وجودة الحياة.

ما هو المفصل الصناعي؟
المفصل الصناعي يتكون من سبائك معدنية طبية فائقة التوافق الحيوي (مثل الكوبالت والكروم والتيتانيوم) مع بطانة مصنوعة من بولي إيثيلين عالي الكثافة تعمل كوسادة بديلة للغضروف المتآكل.

كم تدوم المفاصل الصناعية الحديثة؟
تظهر الدراسات السريرية الموثوقة أن أكثر من 90% إلى 95% من مفاصل الركبة الصناعية الحديثة تستمر في العمل بكفاءة ممتازة لأكثر من 20 إلى 25 سنة، شريطة اتباع إرشادات الطبيب والحفاظ على وزن صحي وتجنب الرياضات العنيفة.

مراحل التعافي:
- في الأيام الأولى: يبدأ المريض بالمشي بمساعدة أخصائي العلاج الطبيعي خلال 24 ساعة من الجراحة.
- خلال 4 إلى 6 أسابيع: يستعيد معظم المرضى القدرة على قيادة السيارة وممارسة الأنشطة اليومية الخفيفة.
- النتيجة النهائية: التخلص شبه التام من الألم المزمن والقدرة على المشي لعدة كيلومترات براحة تامة.''',
                'content_en': 'Comprehensive clinical overview of total knee replacement procedures, implant longevity, and recovery trajectory.',
                'author': admin_user,
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=5),
            },
            {
                'category': blog_cat_joints,
                'title_ar': 'أسباب خشونة المفاصل وكيف تحمي ركبتيك في سن الأربعين والخمسين',
                'title_en': 'Causes of Osteoarthritis and Prevention Strategies',
                'slug': 'osteoarthritis-causes-prevention',
                'excerpt_ar': 'نصائح وقائية هامة لتقليل الضغط على مفاصل الركبة والحوض وتأخير التآكل الغضروفي من خلال التغذية والرياضة الصحية.',
                'excerpt_en': 'Key preventive tips to reduce joint wear and tear and maintain strong cartilage through middle age.',
                'content_ar': '''تعد خشونة المفاصل (Osteoarthritis) التحدي الأكثر شيوعاً بين أمراض الجهاز الحركي. يحدث هذا التآكل نتيجة عوامل متعددة، منها التقدم في العمر، زيادة الوزن، العوامل الوراثية، والإصابات الرياضية القديمة.

أهم طرق الوقاية والحفاظ على المفاصل:
1. تقليل الوزن الزائد: كل كيلوغرام إضافي في وزن الجسم يفرض ضغطاً يعادل 4 كيلوغرامات على مفصل الركبة أثناء المشي.
2. تقوية العضلات المحيطة بالمفصل: وخاصة عضلات الفخذ الأمامية (الرباعية) والخلفية، حيث تعمل كممتص طبيعي للصدمات.
3. تجنب وضعيات الجلوس الخاطئة: مثل ثني الركبتين لفترات طويلة أو الجلوس على الأرض دون دعم مناسب.
4. ممارسة الرياضات منخفضة التأثير: مثل السباحة، وركوب الدراجة الثابتة، والمشي على أسطح مستوية غير صلبة.''',
                'content_en': 'Detailed guidance on preserving joint health and mitigating osteoarthritis progression.',
                'author': admin_user,
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=2),
            }
        ]

        for a_data in articles_data:
            Article.objects.update_or_create(
                slug=a_data['slug'],
                defaults=a_data
            )

        # 10. Realistic Seed Appointments (to ensure real dashboard charts & tables)
        patients_sample = [
            {'name': 'عبدالرحمن سالم باحاج', 'phone': '+967 771 234 567', 'email': 'bahaj@example.com'},
            {'name': 'أمينة عبدالله الحداد', 'phone': '+967 773 456 789', 'email': 'amina@example.com'},
            {'name': 'خالد محمد العواضي', 'phone': '+967 770 987 654', 'email': 'awadhi@example.com'},
            {'name': 'مريم أحمد الصنعاني', 'phone': '+967 775 112 233', 'email': ''},
            {'name': 'يحيى قاسم الردماني', 'phone': '+967 772 889 900', 'email': 'radmani@example.com'},
        ]

        sample_patients_objs = []
        for p in patients_sample:
            pat_obj, _ = Patient.objects.get_or_create(
                phone_number=p['phone'],
                defaults={'full_name': p['name'], 'email': p['email']}
            )
            sample_patients_objs.append(pat_obj)

        srv_list = list(MedicalService.objects.all())
        today = date.today()

        # Create upcoming and past realistic appointments
        apts_sample = [
            # Pending request for tomorrow
            {
                'patient': sample_patients_objs[0],
                'branch': branch,
                'service': srv_list[0] if srv_list else None,
                'date': today + timedelta(days=1),
                'time': time(9, 20),
                'status': Appointment.Status.PENDING,
                'reason': 'استشارة حول آلام شديدة بالركبة اليمنى وصعوبة المشي',
            },
            # Confirmed for tomorrow
            {
                'patient': sample_patients_objs[1],
                'branch': branch,
                'service': srv_list[1] if len(srv_list) > 1 else None,
                'date': today + timedelta(days=1),
                'time': time(10, 0),
                'status': Appointment.Status.CONFIRMED,
                'reason': 'متابعة وفحص الأشعة لمفصل الورك بعد التآكل',
            },
            # Confirmed for day after tomorrow
            {
                'patient': sample_patients_objs[2],
                'branch': branch,
                'service': srv_list[2] if len(srv_list) > 2 else None,
                'date': today + timedelta(days=2),
                'time': time(16, 40),
                'status': Appointment.Status.CONFIRMED,
                'reason': 'تقييم إصابة رياضية واشتباه تمزق في الغضروف الهلالي',
            },
            # Completed appointment in the past
            {
                'patient': sample_patients_objs[3],
                'branch': branch,
                'service': srv_list[0] if srv_list else None,
                'date': today - timedelta(days=3),
                'time': time(11, 20),
                'status': Appointment.Status.COMPLETED,
                'reason': 'فحص دوري للمفصل الصناعي وتغيير الضماد',
            },
            # Cancelled appointment
            {
                'patient': sample_patients_objs[4],
                'branch': branch,
                'service': srv_list[3] if len(srv_list) > 3 else None,
                'date': today - timedelta(days=1),
                'time': time(17, 0),
                'status': Appointment.Status.CANCELLED,
                'reason': 'طلب تأجيل الموعد بسبب السفر',
            },
        ]

        for item in apts_sample:
            apt, created = Appointment.objects.get_or_create(
                patient=item['patient'],
                appointment_date=item['date'],
                appointment_time=item['time'],
                defaults={
                    'branch': item['branch'],
                    'service': item['service'],
                    'status': item['status'],
                    'visit_reason': item['reason'],
                }
            )
            if created:
                AppointmentStatusHistory.objects.create(
                    appointment=apt,
                    old_status='',
                    new_status=item['status'],
                    notes='حجز أولي مجدول بالعيادة'
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded complete realistic clinic dataset!'))

