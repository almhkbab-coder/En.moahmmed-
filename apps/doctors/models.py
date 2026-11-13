from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.validators import validate_image_file


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_profile',
        verbose_name=_('حساب المستخدم المرتبط')
    )
    name_ar = models.CharField(_('اسم الطبيب (عربي)'), max_length=200, default='الدكتور محمد الصياد')
    name_en = models.CharField(_('اسم الطبيب (إنجليزي)'), max_length=200, default='Dr. Mohammed Al-Sayyad')
    
    title_ar = models.CharField(_('اللقب المهني (عربي)'), max_length=200, default='استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية')
    title_en = models.CharField(_('اللقب المهني (إنجليزي)'), max_length=200, default='Consultant in Orthopedic Surgery, Trauma, Pelvis & Artificial Joints')
    
    specialty_ar = models.CharField(_('التخصص الدقيق (عربي)'), max_length=255, default='جراحة استبدال المفاصل الصناعية للركبة والحوض وتقنيات الروبوت وكسور الحوض')
    specialty_en = models.CharField(_('التخصص الدقيق (إنجليزي)'), max_length=255, default='Knee & Hip Arthroplasty, Robotic-Assisted Surgery & Pelvic Fractures')
    
    bio_ar = models.TextField(
        _('السيرة الذاتية والنبذة التعريفية (عربي)'),
        default='الدكتور محمد الصياد استشاري جراحة العظام والكسور والحوض والمفاصل الصناعية، وأستاذ جراحة العظام بكلية الطب – جامعة صنعاء، يمتلك خلفية علمية وتخصصية متقدمة في مجال جراحة العظام، مع اهتمام خاص بجراحات استبدال المفاصل الصناعية للركبة والحوض، وتقنيات المفاصل الصناعية باستخدام الروبوت.\n\nحصل الدكتور محمد الصياد على مؤهلات علمية وتخصصية من عدد من المؤسسات والجامعات الطبية، واكتسب خبرات متقدمة في جراحة العظام وجراحات المفاصل الصناعية، من خلال الدراسات العليا والزمالات والتدريب التخصصي داخل وخارج اليمن.\n\nويُعد من الأطباء اليمنيين الرواد في مجال التخصص الدقيق للمفاصل الصناعية، وخاصة مفاصل الركبة والحوض، ويسعى إلى توظيف أحدث التقنيات والأساليب الجراحية الحديثة لتقديم رعاية طبية متقدمة، والمساهمة في تحسين جودة حياة المرضى واستعادة قدرتهم على الحركة والنشاط.\n\nكما يعمل مدرباً معتمداً للجامعة السويسرية لجراحة العظام في منطقة الشرق الأوسط وشمال أفريقيا، ويساهم في نقل الخبرات والمعرفة الطبية المتخصصة وتطوير الممارسات الجراحية الحديثة.'
    )
    bio_en = models.TextField(
        _('السيرة الذاتية والنبذة التعريفية (إنجليزي)'),
        default='Dr. Mohammed Al-Sayyad is a Consultant Orthopedic, Trauma, Pelvis, and Artificial Joint Surgeon, and Professor of Orthopedic Surgery at the Faculty of Medicine - Sana\'a University. He possesses an advanced academic and clinical background in orthopedics, with specialized focus on knee and hip arthroplasty, and robotic-assisted joint replacement techniques.\n\nHe has earned specialized postgraduate qualifications and fellowships from renowned medical institutions inside and outside Yemen. He is regarded as one of Yemen\'s pioneers in precision joint replacement, dedicated to employing advanced surgical technologies to relieve pain and restore patient mobility.\n\nHe also serves as a certified trainer for the Swiss Orthopaedics University in the Middle East and North Africa (MENA) region.'
    )

    vision_ar = models.TextField(
        _('الرؤية والرسالة الطبية (عربي)'),
        default='تقديم رعاية طبية متخصصة في جراحة العظام والمفاصل، تعتمد على الخبرة العلمية والتقنيات الجراحية الحديثة، بهدف تخفيف الألم، واستعادة الحركة، وتحسين جودة حياة المرضى، وفق أعلى معايير الممارسة الطبية.'
    )
    vision_en = models.TextField(
        _('الرؤية والرسالة الطبية (إنجليزي)'),
        default='Providing specialized orthopedic and joint medical care based on scientific expertise and modern surgical techniques, aiming to relieve pain, restore mobility, and improve patients\' quality of life in accordance with the highest medical standards.'
    )
    
    profile_photo = models.ImageField(_('الصورة الشخصية الرسمية'), upload_to='doctors/profile/', blank=True, null=True, validators=[validate_image_file])
    hero_photo = models.ImageField(_('صورة الواجهة الرئيسية'), upload_to='doctors/hero/', blank=True, null=True, validators=[validate_image_file])
    
    # Real metrics/stats
    years_of_experience = models.PositiveIntegerField(_('سنوات الخبرة الطبية'), default=15)
    successful_surgeries = models.PositiveIntegerField(_('عدد العمليات الجراحية الناجحة'), default=3500)
    consultations_count = models.PositiveIntegerField(_('عدد الاستشارات الطبية'), default=12000)
    
    is_active = models.BooleanField(_('نشط ويعرض في الموقع'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإضافة'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('ملف الطبيب')
        verbose_name_plural = _('ملف الطبيب')

    def __str__(self):
        return self.name_ar


class Education(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='educations', verbose_name=_('الطبيب'))
    degree_ar = models.CharField(_('الدرجة العلمية / المؤهل (عربي)'), max_length=255)
    degree_en = models.CharField(_('الدرجة العلمية / المؤهل (إنجليزي)'), max_length=255)
    institution_ar = models.CharField(_('الجامعة / الكلية (عربي)'), max_length=255)
    institution_en = models.CharField(_('الجامعة / الكلية (إنجليزي)'), max_length=255)
    year = models.CharField(_('سنة التخرج أو الحصول عليه'), max_length=50, blank=True, default='')
    order = models.PositiveIntegerField(_('الترتيب'), default=0)

    class Meta:
        verbose_name = _('مؤهل علمي')
        verbose_name_plural = _('المؤهلات العلمية')
        ordering = ['order', '-year']

    def __str__(self):
        return f"{self.degree_ar} - {self.institution_ar}"


class Experience(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='experiences', verbose_name=_('الطبيب'))
    position_ar = models.CharField(_('المسمى الوظيفي (عربي)'), max_length=255)
    position_en = models.CharField(_('المسمى الوظيفي (إنجليزي)'), max_length=255)
    hospital_ar = models.CharField(_('المستشفى / المركز الطبي (عربي)'), max_length=255)
    hospital_en = models.CharField(_('المستشفى / المركز الطبي (إنجليزي)'), max_length=255)
    period_ar = models.CharField(_('الفترة الزمنية (عربي)'), max_length=100)
    period_en = models.CharField(_('الفترة الزمنية (إنجليزي)'), max_length=100)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)

    class Meta:
        verbose_name = _('خبرة مهنية')
        verbose_name_plural = _('الخبرات المهنية')
        ordering = ['order']

    def __str__(self):
        return f"{self.position_ar} - {self.hospital_ar}"


class Certificate(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='certificates', verbose_name=_('الطبيب'))
    title_ar = models.CharField(_('عنوان الشهادة أو العضوية (عربي)'), max_length=255)
    title_en = models.CharField(_('عنوان الشهادة أو العضوية (إنجليزي)'), max_length=255)
    issuer_ar = models.CharField(_('الجهة المانحة (عربي)'), max_length=255)
    issuer_en = models.CharField(_('الجهة المانحة (إنجليزي)'), max_length=255)
    year = models.CharField(_('سنة الحصول'), max_length=50, blank=True)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)

    class Meta:
        verbose_name = _('شهادة / عضوية مهنية')
        verbose_name_plural = _('الشهادات والعضويات المهنية')
        ordering = ['order']

    def __str__(self):
        return self.title_ar

