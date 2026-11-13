# دليل المطورين ونماذج الذكاء الاصطناعي لفهم بنية المشروع
# AI Models & Developers Master Architecture Guide

**مشروع:** الموقع الطبي ونظام إدارة عيادة الدكتور محمد أحمد الصياد  
**التخصص:** جراحة العظام والمفاصل الصناعية (Orthopedic Surgery & Artificial Joint Replacement)  
**المقر:** صنعاء، الجمهورية اليمنية  
**التقنيات:** Python 3.12 / Django 5.2 LTS / PostgreSQL / Tailwind CSS / Vanilla JS  

---

## 1. فهرس وخرائط وثائق المشروع الموحدة (Directory of Documentation)

جميع ملفات التوثيق متمركزة في مجلد `docs/` لتسهيل الفهرسة والوصول السريع:

| اسم الملف | التصنيف | الوصف والغرض التقني |
| :--- | :--- | :--- |
| [`DEVELOPER_AND_AI_GUIDE.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/DEVELOPER_AND_AI_GUIDE.md) | **دليل شامل** | الدليل الأساسي لفهم المعمارية، قواعد البيانات، الأمان، والتوجيه للنماذج والمطورين. |
| [`PROJECT_COMPREHENSIVE_REPORT.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PROJECT_COMPREHENSIVE_REPORT.md) | **المرحلة 1** | تقرير التنفيذ الأساسي للبنية الهيكلية، التطبيقات، النماذج، والواجهات. |
| [`PHASE_2_AUDIT_AND_SECURITY_REPORT.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PHASE_2_AUDIT_AND_SECURITY_REPORT.md) | **المرحلة 2** | تقرير التدقيق التقني، التصليد الأمني، وحماية التوثيق ورفع الملفات. |
| [`PHASE_3_STAGING_REPORT.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PHASE_3_STAGING_REPORT.md) | **المرحلة 3** | تقرير النشر في بيئة الاختبار (Staging)، وتجربة الاستعادة والنسخ الاحتياطي. |
| [`PHASE_4_PRODUCTION_READINESS_REPORT.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PHASE_4_PRODUCTION_READINESS_REPORT.md) | **المرحلة 4** | تقرير تدقيق الجاهزية للإنتاج، فحص تسريب السجلات، واجتياز 37 اختباراً آلياً. |
| [`OFFICIAL_DOCTOR_PROFILE_UPDATE_REPORT.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/OFFICIAL_DOCTOR_PROFILE_UPDATE_REPORT.md) | **المرحلة 4A** | تقرير التحديث الرسمي لبيانات الطبيب، حذف الأرقام التجريبية، وإعادة هيكلة الصفحات الست والشعار والصورة. |
| [`DATABASE.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/DATABASE.md) | **قواعد البيانات** | المخطط الشامل للجداول، القيود العلائقية، الفهارس، واستراتيجية التخزين. |
| [`BACKUP_RESTORE_VERIFICATION.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/BACKUP_RESTORE_VERIFICATION.md) | **العمليات (Ops)** | سجل وتقرير تمرين النسخ الاحتياطي والاستعادة الفعلي على قاعدة بيانات منفصلة. |
| [`DISASTER_RECOVERY_PLAN_AR.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/DISASTER_RECOVERY_PLAN_AR.md) | **التعافي من الكوارث** | خطة استمرارية الأعمال، معايير RTO و RPO، وإجراءات الطوارئ الفنية. |
| [`STAGING_DEPLOYMENT_GUIDE.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/STAGING_DEPLOYMENT_GUIDE.md) | **دليل النشر** | خطوات نشر وتشغيل بيئة الفحص المسبق (Staging Server Setup). |
| [`PRODUCTION_DEPLOYMENT_GUIDE.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PRODUCTION_DEPLOYMENT_GUIDE.md) | **دليل النشر** | الدليل المتكامل لإعداد خادم الإنتاج (Nginx, Gunicorn, PostgreSQL, SSL, Systemd). |
| [`PRODUCTION_SECURITY_CHECKLIST_AR.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PRODUCTION_SECURITY_CHECKLIST_AR.md) | **الأمان** | قائمة التحقق الأمني لبيئة الإنتاج (التشفير، الجلسات، الترويسات، الحسابات). |
| [`CLINIC_OWNER_APPROVAL_CHECKLIST_AR.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/CLINIC_OWNER_APPROVAL_CHECKLIST_AR.md) | **الاعتماد الإداري** | بنود مراجعة واعتماد الدكتور محمد الصياد للبيانات الطبية والإحصاءات الحقيقية. |
| [`FINAL_GO_LIVE_CHECKLIST_AR.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/FINAL_GO_LIVE_CHECKLIST_AR.md) | **الإطلاق** | قائمة التحقق اللحظية ليوم إطلاق الموقع الحي خطوة بخطوة. |
| [`DOCTOR_GUIDE_AR.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/DOCTOR_GUIDE_AR.md) | **دليل استخدام** | دليل استخدام بوابة الطبيب: إدارة المواعيد، الكشف الطبي، والتقارير. |
| [`CLINIC_ADMIN_GUIDE_AR.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/CLINIC_ADMIN_GUIDE_AR.md) | **دليل استخدام** | دليل مدير العيادة: إدارة الفروع، الأطباء، الصلاحيات، وإعدادات العيادة. |
| [`RECEPTIONIST_GUIDE_AR.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/RECEPTIONIST_GUIDE_AR.md) | **دليل استخدام** | دليل موظف الاستقبال: استقبال المرضى، تأكيد الحجوزات، وجدولة المواعيد. |

---

## 2. الهيكلية المعمارية للنظام (Architecture Overview)

المشروع مبني وفق معمارية Django المعيارية النظيفة (Modular Clean Architecture) ومقسم إلى 5 تطبيقات رئيسية داخل مجلد `apps/`:

```
d:\DR.MOHAMMED ALSAYYAD/
├── apps/
│   ├── core/              # البنية المشتركة، التشفير، سجلات النشاط، الصفحات العامة
│   ├── appointments/      # محرك إدارة المواعيد، الفروع، منع التضارب، والجدولة
│   ├── accounts/          # إدارة المستخدمين، الأدوار والصلاحيات، ولوحات التحكم
│   ├── patients/          # ملفات المرضى المشفرة، التاريخ المرضي، والزيارات
│   └── blog/              # المقالات الطبية التثقيفية، التصنيفات، وإعدادات SEO
├── config/
│   ├── settings/
│   │   ├── base.py        # الإعدادات العامة والتطبيقات المشتركة
│   │   ├── development.py # إعدادات التطوير المحلي
│   │   ├── staging.py     # إعدادات بيئة الفحص والتجربة
│   │   └── production.py  # إعدادات بيئة الإنتاج المصلدة أمنياً
│   ├── urls.py            # توجيه الروابط العام ودعم اللغتين (i18n)
│   └── wsgi.py            # واجهة تشغيل الخادم
├── docs/                  # التوثيق الشامل ومراجع النماذج والمطورين
├── templates/             # قوالب HTML تدعم RTL (العربية) و LTR (الإنجليزية)
├── static/                # ملفات التصميم والأيقونات والخطوط وسكربتات JS
└── tests/                 # جناح الاختبارات الآلية الشامل (37 اختباراً ناجحاً)
```

---

## 3. محرك المواعيد وقواعد منع التضارب (Appointments Engine)

### المعادلة الرياضية لمنع التداخل الزمني:
لكي يعتبر موعدان $A$ و $B$ متداخلين زمنياً لنفس الفرع (`branch`)، يجب تحقق الشرط التالي:
$$\text{Start}_A < \text{End}_B \land \text{Start}_B < \text{End}_A$$

### الحماية المزدوجة (Application + Database):
1. **على مستوى التطبيق (`apps/appointments/services.py`):**
   - فحص استباقي داخل معاملة ذرية `transaction.atomic()` مع قفل الصفوف لمنع حالات السباق (`select_for_update`).
2. **على مستوى قاعدة البيانات (PostgreSQL Constraint):**
   - قيد فريد شرطي يمنع تكرار المواعيد المؤكدة لنفس الفرع والوقت:
     ```python
     UniqueConstraint(
         fields=['branch', 'appointment_date', 'appointment_time'],
         condition=Q(status='confirmed'),
         name='unique_confirmed_appointment_per_branch_slot'
     )
     ```
3. **معالجة التزامن (Concurrency Exception Handling):**
   - في حال حدث تصادم تزامني لحظي، يلتقط النظام `IntegrityError` ويعيد للمستخدم رسالة خطأ تحقق `ValidationError` واضحة ومترجمة مع ضمان التراجع التام للمعاملة.

---

## 4. الخصوصية والأمان والتشفير (Security & Privacy Standards)

### تشفير بيانات المرضى الحساسة:
- الخوارزمية المستخدمة: **Fernet Specification**.
- التفصيل الرياضي والتقني الدقيق:
  - **AES-128-CBC** لتشفير البيانات مع حشو **PKCS7**.
  - **HMAC-SHA256** للتحقق من سلامة وصحة التشفير والمصادقة.
  - مفتاح مركب بطول **32 بايت** (256-bit URL-safe base64-encoded).
  - *تنبيه هندسي للنماذج:* لا يتم وصف الخوارزمية بأنها AES-256، بل **AES-128-CBC + HMAC-SHA256**.
- عزل المفاتيح: المفتاح مخزن حصرياً في بيئة التشغيل كمتغير بيئي `PATIENT_DATA_ENCRYPTION_KEY` وغير مدرج بقاعدة البيانات أو الكود المصدري.

### سياسة حظر تسريب السجلات (Zero-Leak Logging):
- يمنع منعاً باتاً تسجيل الاسم الصريح للمريض أو رقم هاتفه أو أي ملاحظات طبية تشخيصية في ملفات السجلات (`logs/`) أو جدول نشاط النظام (`ActivityLog`).
- يُسمح فقط بتسجيل الرقم المرجعي العام للموعد (مثل: `APT-9B2F4C1A`) وتاريخ الحجز.

### أمان رفع الملفات:
- حظر امتداد ووسائط SVG بالكامل لمنع ثغرات XSS المخزنة وحقن XML.
- فحص عميق للمحتوى الداخلي للصور عبر مكتبة Pillow للتأكد من أنها صور رقمية فعلية صالحة وليست برمجيات خبيثة مقنعة.

---

## 5. الأدوار والصلاحيات (Role-Based Access Control)

النظام يعتمد نموذج مستخدم مخصص [`apps/accounts/models.py`](file:///d:/DR.MOHAMMED%20ALSAYYAD/apps/accounts/models.py) بالصلاحيات التالية:

1. **مدير النظام العام (Super Administrator / Clinic Owner):**
   - وصول كامل لجميع لوحات الإدارة، التقارير المالية، إعدادات الفروع، وتعيين الطاقم.
2. **الطبيب (Doctor - د. محمد أحمد الصياد):**
   - وصول كامل لجدول المواعيد الخاص به، الكشف الطبي، كتابة التشخيص والوصفات، واستعراض التاريخ المرضي.
3. **موظف الاستقبال (Receptionist):**
   - تسجيل المواعيد وتأكيدها أو إلغاؤها، تسجيل حضور المريض، البحث عن المواعيد عبر الرقم المرجعي، دون صلاحية تعديل السجلات الطبية.
4. **مدير المحتوى (Content Manager):**
   - إدارة ونشر المقالات الطبية والتوعوية في المدونة، والرد على استفسارات الموقع العامة.

---

## 6. أوامر التطوير والتشغيل السريعة (Developer Quick Reference)

### إعداد البيئة وتشغيل الخادم:
```bash
# تثبيت الاعتماديات
pip install -r requirements.txt

# تشغيل بيئة التطوير
python manage.py runserver --settings=config.settings.development

# تطبيق ترحيلات قاعدة البيانات
python manage.py migrate --settings=config.settings.development
```

### تشغيل الاختبارات الآلية الشاملة:
```bash
# تشغيل كامل جناح الاختبارات (37 اختباراً)
python manage.py test tests

# تشغيل فحص الجاهزية للإنتاج
python manage.py test tests.test_phase4_production_readiness
```

### الفحص الأمني للإنتاج:
```bash
python manage.py check --deploy --settings=config.settings.production
```

---

## 7. إرشادات خاصة بنماذج الذكاء الاصطناعي (Guidelines for AI Agents)

عند قيام أي نموذج ذكاء اصطناعي (LLM) بتعديل أو إضافة ميزات لهذا المشروع، يجب الالتزام بالقواعد الصارمة التالية:
1. **الحفاظ على التدويل (i18n):** أي نص جديد للواجهات يجب تغليفه بـ `gettext_lazy` أو `gettext` لدعم اللغتين العربية والإنجليزية.
2. **عدم المساس بالقيود التزامنية:** لا تقم بإزالة `transaction.atomic()` أو القيد `unique_confirmed_appointment_per_branch_slot` من محرك المواعيد.
3. **الامتثال للخصوصية:** لا تضع أسماء المرضى في سجلات الأنشطة `ActivityLog` أو `logger.info`.
4. **التأكد من اجتياز الاختبارات:** تشغيل `python manage.py test tests` للتأكد من عدم كسر أي من الاختبارات الـ 37 القائمة.

