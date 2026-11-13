# الموقع الطبي الرسمي ونظام إدارة العيادة وحجوزات المواعيد
## الدكتور محمد أحمد الصياد | استشاري جراحة العظام والمفاصل الصناعية
### Dr. Mohammed Ahmed Al-Sayyad Clinic & Medical Management System

---

## 📚 مركز التوثيق الشامل ومجلد الوثائق الموحد (`docs/`)
تم تجميع وهيكلة جميع الوثائق والتقارير الفنية وأدلة التشغيل والأمان في مجلد واحد موحد [`docs/`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs):
- 📘 **دليل المطورين ونماذج الذكاء الاصطناعي الرئيسي:** [`docs/DEVELOPER_AND_AI_GUIDE.md`](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/DEVELOPER_AND_AI_GUIDE.md)
- 📊 **تقارير المراحل التنفيذية (Phases 1-4):**
  - [تقرير المرحلة 1 - التنفيذ الأساسي](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PROJECT_COMPREHENSIVE_REPORT.md)
  - [تقرير المرحلة 2 - التدقيق التقني والتصليد الأمني](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PHASE_2_AUDIT_AND_SECURITY_REPORT.md)
  - [تقرير المرحلة 3 - بيئة الفحص والتجربة واختبار الاستعادة](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PHASE_3_STAGING_REPORT.md)
  - [تقرير المرحلة 4 - تدقيق الجاهزية للإنتاج واعتماد النشر](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PHASE_4_PRODUCTION_READINESS_REPORT.md)
  - [تقرير المرحلة 4A - التحديث الرسمي لبيانات الطبيب وإعادة هيكلة الموقع](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/OFFICIAL_DOCTOR_PROFILE_UPDATE_REPORT.md)
- ⚙️ **أدلة النشر والعمليات والتعافي:**
  - [دليل نشر بيئة الاختبار Staging](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/STAGING_DEPLOYMENT_GUIDE.md)
  - [دليل نشر بيئة الإنتاج Production](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PRODUCTION_DEPLOYMENT_GUIDE.md)
  - [تقرير تمرين النسخ الاحتياطي والاستعادة](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/BACKUP_RESTORE_VERIFICATION.md)
  - [خطة التعافي من الكوارث واستمرارية الأعمال](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/DISASTER_RECOVERY_PLAN_AR.md)
- 🛡️ **قوائم التدقيق الأمني والاعتمادات:**
  - [قائمة التدقيق الأمني للإنتاج](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/PRODUCTION_SECURITY_CHECKLIST_AR.md)
  - [قائمة اعتماد وموافقة مالك العيادة د. محمد الصياد](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/CLINIC_OWNER_APPROVAL_CHECKLIST_AR.md)
  - [قائمة التحقق اللحظية ليوم الإطلاق الحي](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/FINAL_GO_LIVE_CHECKLIST_AR.md)
- 👥 **أدلة المستخدمين حسب الأدوار:**
  - [دليل الطبيب](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/DOCTOR_GUIDE_AR.md)
  - [دليل مدير النظام](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/CLINIC_ADMIN_GUIDE_AR.md)
  - [دليل موظف الاستقبال](file:///d:/DR.MOHAMMED%20ALSAYYAD/docs/RECEPTIONIST_GUIDE_AR.md)

---

## 1. نظرة عامة على المشروع (Project Overview)

نظام برمجي متكامل تم بناؤه بأحدث المعايير الطبية والبرمجية لتقديم واجهة طبية احترافية ثنائية اللغة (عربي/إنجليزي مع أولوية كاملة للغة العربية ودعم RTL دقيق) لعيادة الدكتور محمد أحمد الصياد في صنعاء، اليمن، مصحوباً بنظام متطور لإدارة المواعيد وحجوزات المرضى ولوحة تحكم مخصصة لإدارة العمليات والمحتوى والخدمات الطبية والمكتبة التثقيفية المرئية.

### هوية المشروع
- **اسم الطبيب:** الدكتور محمد أحمد الصياد (Dr. Mohammed Ahmed Al-Sayyad)
- **التخصص:** استشاري جراحة العظام والمفاصل الصناعية (Orthopedic Surgery and Artificial Joint Replacement)
- **اسم العيادة:** عيادة الدكتور محمد الصياد
- **الموقع الجغرافي:** صنعاء، اليمن - شارع الزبيري
- **اللغات المدعومة:** العربية (الافتراضية والأساسية) والإنجليزية مع مبدل لغة فوري وتنسيقات RTL/LTR متوافقة.

---

## 2. التقنيات المستخدمة (Technology Stack)

### الخلفية البرمجية (Backend)
- **Python 3.12+**
- **Django 5.1+ LTS**
- **PostgreSQL 18** (مع دعم تشفير UTF-8 والفهارس المركبة والمعاملات الذرية `transaction.atomic` وقفل الصفوف `select_for_update`)
- **Pillow** لمعالجة وتحسين الصور المرفوعة
- **python-dotenv** لإدارة المتغيرات البيئية الحساسة بأمان
- **WhiteNoise** لإدارة وتقديم الملفات الثابتة بسرعة عالية

### الواجهة الأمامية وتجربة المستخدم (Frontend UI/UX)
- **HTML5 & CSS3** الدلالي المتوافق مع معايير الوصول العالمية
- **Bootstrap 5 (RTL & LTR)**
- **Bootstrap Icons**
- **الخطوط الطبية الرسمية:** Cairo و Tajawal للغة العربية، و Inter للغة الإنجليزية
- **JavaScript (Vanilla Fetch API)** لجلب وتوليد فترات المواعيد اللحظية ديناميكياً
- **Chart.js** للرسوم البيانية التفاعلية وتحليل أداء الحجوزات

### محركات البحث والأرشفة (Google SEO)
- **Schema.org Structured Data (JSON-LD)** لأنواع `Physician`, `MedicalClinic`, `MedicalWebPage`, `Article`
- **Dynamic Multilingual Sitemap.xml** لأرشفة كافة الخدمات والمقالات والسلاسل والصفحات الثابتة
- **Robots.txt** مع حجب الصفحات الإدارية ولوحة التحكم
- وسوم Open Graph و Twitter Cards للمشاركة عبر وسائل التواصل

---

## 3. هيكل المشروع (Project Architecture)

```
d:\DR.MOHAMMED ALSAYYAD\
├── config\                     # ضبط إعدادات جانغو
│   ├── settings\
│   │   ├── base.py             # الإعدادات العامة وقاعدة البيانات PostgreSQL
│   │   ├── development.py      # إعدادات بيئة التطوير
│   │   └── production.py       # إعدادات الإنتاج والأمان العالي
│   ├── urls.py                 # موجه الروابط الرئيسي
│   ├── wsgi.py                 # واجهة خادم الإنتاج WSGI
│   └── asgi.py
├── apps\                       # التطبيقات المستقلة
│   ├── accounts\               # المستخدم المخصص والصلاحيات (Admin, Doctor, Receptionist)
│   ├── core\                   # إعدادات الموقع العامة وسجل النشاط الرقابي (ActivityLog)
│   ├── doctors\                # ملف الطبيب، المؤهلات، والخبرات السريرية
│   ├── clinics\                # الفروع، أوقات العمل الصباحية والمسائية، والعطلات
│   ├── services\               # الخدمات الطبية وجراحة العظام والمفاصل
│   ├── education\              # السلاسل التوعوية وحلقات وفيديوهات YouTube
│   ├── blog\                   # المقالات الطبية، أوقات القراءة، وإخلاء المسؤولية الطبية
│   ├── appointments\           # سجلات المرضى، محرك الفترات الزمنية، وحجوزات المواعيد
│   ├── contact\                # رسائل واستفسارات الاتصال مع حماية Honeypot
│   ├── dashboard\              # لوحة التحكم الإدارية والتحليلات البيانية
│   └── seo\                    # خرائط الموقع XML و Robots.txt وبيانات Schema.org
├── static\                     # الأصول الثابتة
│   ├── css\medical_theme.css   # نظام الألوان والأنماط الطبية الرسمية
│   ├── js\
│   └── img\
├── media\                      # ملفات الوسائط والصور المرفوعة
├── templates\                  # القوالب المصممة
│   ├── base.html               # القالب العام للواجهة العامة
│   ├── partials\               # القوائم والفوتر والرسائل
│   ├── public\                 # واجهات الموقع العامة (الرئيسية، عن الطبيب، الخدمات، الحجز...)
│   └── dashboard\              # واجهات لوحة التحكم الإدارية
├── tests\                      # حزمة الاختبارات المؤتمتة الشاملة
├── gunicorn_config.py          # ملف تشغيل Gunicorn للإنتاج
├── nginx_clinic.conf           # إعدادات ملقم Nginx العكسي وشهادات SSL
├── requirements.txt            # المكتبات والتبعيات
├── DATABASE.md                 # التوثيق المفصل لقاعدة البيانات
└── README.md
```

---

## 4. متطلبات التشغيل والتثبيت (Installation Guide)

### 1. المتطلبات المسبقة
- تثبيت Python 3.12 أو أحدث.
- خادم PostgreSQL شغال (تم تهيئة قاعدة بيانات `alsayyad_clinic_db`).

### 2. تثبيت الحزم البرمجية
```bash
pip install -r requirements.txt
```

### 3. إعداد ملف البيئة (`.env`)
تأكد من وجود ملف `.env` في مجلد المشروع الرئيسي بالقيم الصحيحة:
```ini
SECRET_KEY=django-insecure-alsayyad-ortho-clinic-secret-key-2026-production-ready
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]

DB_ENGINE=django.db.backends.postgresql
DB_NAME=alsayyad_clinic_db
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=127.0.0.1
DB_PORT=5432

TIME_ZONE=Asia/Aden
LANGUAGE_CODE=ar
```

### 4. تطبيق ترحيل قاعدة البيانات (Migrations)
```bash
python manage.py migrate
```

### 5. زراعة البيانات الأولية وتعيين كلمات المرور الآمنة (Seed Data)
يقوم هذا الأمر بتجهيز كامل الخدمات الطبية، مؤهلات الطبيب، مواعيد العمل الرسمية بصنعاء، مقالات المدونة، وحسابات المشرفين بأمان:
```bash
# يمكن تمرير كلمات المرور الأولية عبر متغيرات البيئة قبل التشغيل:
# set ADMIN_INITIAL_PASSWORD=YourSecurePass123!
# set RECEPTION_INITIAL_PASSWORD=YourSecureReception456!
python manage.py seed_clinic_data
```
> **ملاحظة أمنية (Phase 2 Security):** في حال عدم تحديد كلمات المرور مسبقاً، يقوم الأمر بتوليد كلمات مرور عشوائية قوية وطباعتها على الطرفية لمرة واحدة فقط لضمان عدم وجود بيانات اعتماد ثابتة مكشوفة.

---

## 5. إدارة الحسابات والصلاحيات المقيدة (Role-Based Access Control)

تم تطبيق مبدأ الامتيازات الأقل (Least Privilege) والتحقق منها على مستوى خادم الويب:

- **حساب المشرف العام (Super Administrator):**
  - كامل الصلاحيات الإدارية، بما في ذلك إعدادات العيادة وسجلات الرقابة الأمنية (Audit Logs).
  - الرابط: `http://127.0.0.1:8000/dashboard/login/`

- **حساب الطبيب (Doctor):**
  - إدارة السيرة الذاتية، الخدمات الطبية، المقالات، والمواعيد، مع حظر الوصول لإعدادات الموقع العامة وسجلات الرقابة الأمنية.

- **حساب موظف الاستقبال (Receptionist):**
  - مقيد فقط بإدارة حجوزات المواعيد واستفسارات المرضى وتقويم الزيارات، ومحجوب تماماً عن تعديل الخدمات أو إعدادات الموقع أو المقالات.

- **حساب مدير المحتوى (Content Manager):**
  - مقيد بإدارة مقالات المدونة والمكتبة التثقيفية، ومحجوب تماماً عن سجلات المرضى والمواعيد وإعدادات النظام.

> **حماية الهجمات العنيفة (Brute Force Protection):** يتم إغلاق نافذة تسجيل الدخول مؤقتاً (HTTP 429) عند تجاوز 5 محاولات فاشلة متتالية لمدة 15 دقيقة.

---

## 6. تشغيل خادم التطوير (Development Server)

```bash
python manage.py runserver
```

بعد التشغيل، يمكنك فتح المتصفح على:
- الموقع العام: `http://127.0.0.1:8000/`
- شاشة حجز المواعيد: `http://127.0.0.1:8000/booking/`
- متابعة حالة الحجز (استعلام آمن يتطلب رمز الحجز ورقم الهاتف): `http://127.0.0.1:8000/booking/status/`
- لوحة التحكم الإدارية: `http://127.0.0.1:8000/dashboard/`
- لوحة إدارة جانغو: `http://127.0.0.1:8000/admin/`
- خريطة الموقع لمحركات البحث: `http://127.0.0.1:8000/sitemap.xml`
- ملف الروبوتات: `http://127.0.0.1:8000/robots.txt`

---

## 7. تشغيل حزمة الاختبارات الآلية (29 Automated Tests)

تم تضمين حزمة اختبارات شاملة تضم 29 اختباراً مؤتمتاً تغطي:
- أمان المصادقة وتسجيل الدخول والحماية ضد هجمات القوة الغاشمة (Brute Force Lockout).
- الصلاحيات المقيدة (RBAC Least Privilege) ومنع الوصول المباشر عبر الروابط غير المصرح بها (403 Forbidden).
- محرك فحص المواعيد المتاحة ومنع الحجز المزدوج واستبعاد العطلات وساعات الدوام.
- القيد الشرطي على مستوى PostgreSQL لمنع التعارض في الحجوزات المؤكدة.
- حماية حذف سجلات المرضى المرتبطة بمواعيد (`on_delete=models.PROTECT`).
- حماية خصوصية بيانات المرضى وحجب الأسماء الكاملة والملاحظات الداخلية في شاشة الاستعلام.
- حماية النماذج العامة ضد السبام عبر حقول Honeypot وتحديد معدل الطلبات (Rate Limiting).
- التحقق الصارم من امتدادات وحجم الملفات والصور المرفوعة (5MB كحد أقصى).

لتشغيل الاختبارات:
```bash
python manage.py test tests
```

---

## 8. النشر والتشغيل في بيئة الإنتاج (Production Deployment)

1. **تحديث إعدادات الأمان:**
   - ضبط `DEBUG=False` في ملف `.env`.
   - توليد `SECRET_KEY` جديد وعشوائي بالكامل.
   - تحديد نطاق الموقع في `ALLOWED_HOSTS`.

2. **تجميع الملفات الثابتة:**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **تشغيل ملقم Gunicorn:**
   ```bash
   gunicorn -c gunicorn_config.py config.wsgi:application
   ```

4. **إعداد Nginx وشهادة SSL:**
   - نسخ إعدادات `nginx_clinic.conf` إلى `/etc/nginx/sites-available/`.
   - إصدار شهادة Let's Encrypt SSL مجانية عبر Certbot:
     ```bash
     sudo certbot --nginx -d alsayyad-clinic.ye -d www.alsayyad-clinic.ye
     ```

---

## 9. النسخ الاحتياطي واستعادة قاعدة البيانات (Backups)

### إنشاء نسخة احتياطية من PostgreSQL:
```bash
pg_dump -U postgres -h 127.0.0.1 alsayyad_clinic_db > backup_alsayyad_$(date +%Y%m%d).sql
```

### استعادة النسخة الاحتياطية:
```bash
psql -U postgres -h 127.0.0.1 -d alsayyad_clinic_db < backup_alsayyad_YYYYMMDD.sql
```

