# توثيق قاعدة البيانات والهندسة المعمارية | عيادة الدكتور محمد الصياد

## 1. محرك قاعدة البيانات
- **Database Engine:** PostgreSQL 18
- **Encoding:** UTF-8
- **Collation:** Default (مفعل لدعم النصوص العربية والإنجليزية)
- **ORM:** Django 5.1+ ORM مع استخدام Transactions و `select_for_update` لضمان تكامل الحجوزات المتزامنة.

---

## 2. هيكل الجداول والنماذج (Models & Tables)

### تطبيق الحسابات والصلاحيات (accounts)
#### `accounts_customuser`
- `id` (BigAutoField, PK)
- `username` (VARCHAR(150), Unique)
- `email` (EmailField, Unique)
- `password` (VARCHAR(128), PBKDF2 SHA256)
- `role` (VARCHAR(20), Choices: `super_admin`, `doctor`, `receptionist`, `content_manager`)
- `phone_number` (VARCHAR(25))
- `profile_image` (VARCHAR(100), Image path)
- `is_staff`, `is_superuser`, `is_active`, `date_joined`, `last_login`

---

### تطبيق العيادات وساعات العمل (clinics)
#### `clinics_clinic`
- `id` (BigAutoField, PK)
- `name_ar` (VARCHAR(200)), `name_en` (VARCHAR(200))
- `description_ar` (TEXT), `description_en` (TEXT)
- `created_at` (DateTimeField)

#### `clinics_clinicbranch`
- `id` (BigAutoField, PK)
- `clinic_id` (FK -> `clinics_clinic.id`, ON DELETE CASCADE)
- `name_ar` (VARCHAR(200)), `name_en` (VARCHAR(200))
- `city_ar` (VARCHAR(100)), `city_en` (VARCHAR(100))
- `address_ar` (VARCHAR(300)), `address_en` (VARCHAR(300))
- `phone` (VARCHAR(50)), `whatsapp` (VARCHAR(50)), `email` (EmailField)
- `map_embed_url` (TEXT), `latitude` (DECIMAL(9,6)), `longitude` (DECIMAL(9,6))
- `is_primary` (BOOLEAN, default True), `is_active` (BOOLEAN, default True)

#### `clinics_workinghours`
- `id` (BigAutoField, PK)
- `branch_id` (FK -> `clinics_clinicbranch.id`, ON DELETE CASCADE)
- `day_of_week` (INTEGER, Choices: 0=Saturday, 1=Sunday, 2=Monday, 3=Tuesday, 4=Wednesday, 5=Thursday, 6=Friday)
- `morning_start` (TimeField, nullable), `morning_end` (TimeField, nullable)
- `evening_start` (TimeField, nullable), `evening_end` (TimeField, nullable)
- `slot_duration_minutes` (INTEGER, default 20)
- `is_closed` (BOOLEAN, default False)
- **Constraint:** `unique_together = ('branch', 'day_of_week')`

#### `clinics_clinicholiday`
- `id` (BigAutoField, PK)
- `branch_id` (FK -> `clinics_clinicbranch.id`, ON DELETE CASCADE, nullable)
- `date` (DateField)
- `reason_ar` (VARCHAR(255)), `reason_en` (VARCHAR(255))

---

### تطبيق الطبيب والسيرة الذاتية (doctors)
#### `doctors_doctorprofile`
- `id` (BigAutoField, PK)
- `user_id` (OneToOne -> `accounts_customuser.id`, ON DELETE SET_NULL)
- `name_ar`, `name_en`, `title_ar`, `title_en`, `specialty_ar`, `specialty_en`
- `bio_ar` (TEXT), `bio_en` (TEXT)
- `profile_photo`, `hero_photo`
- `years_of_experience` (INTEGER), `successful_surgeries` (INTEGER), `consultations_count` (INTEGER)
- `is_active` (BOOLEAN)

#### `doctors_education`, `doctors_experience`, `doctors_certificate`
- مرتبطة بعلاقة `ForeignKey` مع `DoctorProfile` مع حفظ الترتيب والسنوات والدرجات العلمية باللغتين العربية والإنجليزية.

---

### تطبيق الخدمات الطبية (services)
#### `services_servicecategory`
- `id` (BigAutoField, PK)
- `name_ar`, `name_en`, `slug` (SlugField, Unique), `icon`, `order`, `is_active`

#### `services_medicalservice`
- `id` (BigAutoField, PK)
- `category_id` (FK -> `services_servicecategory.id`, ON DELETE SET_NULL)
- `title_ar`, `title_en`, `slug` (SlugField, Unique)
- `short_desc_ar`, `short_desc_en`, `full_desc_ar`, `full_desc_en`
- `featured_image`, `icon`
- `is_featured` (BOOLEAN), `is_active` (BOOLEAN), `order` (INTEGER)
- `meta_title_ar`, `meta_title_en`, `meta_desc_ar`, `meta_desc_en`

---

### تطبيق المكتبة التثقيفية (education)
#### `education_educationalseries`
- `id` (BigAutoField, PK)
- `title_ar`, `title_en`, `slug` (Unique), `description_ar`, `description_en`, `cover_image`, `is_published`, `order`

#### `education_educationalvideo`
- `id` (BigAutoField, PK)
- `series_id` (FK -> `education_educationalseries.id`, ON DELETE CASCADE)
- `title_ar`, `title_en`, `slug` (Unique)
- `youtube_url` (URLField)
- `youtube_video_id` (VARCHAR(50), مستخرج تلقائياً ومتحقق منه برمجياً)
- `duration_minutes` (INTEGER), `episode_number` (INTEGER)
- `description_ar`, `description_en`, `is_published`

---

### تطبيق المدونة والمقالات الطبية (blog)
#### `blog_article`
- `id` (BigAutoField, PK)
- `category_id` (FK -> `blog_articlecategory.id`)
- `author_id` (FK -> `accounts_customuser.id`)
- `title_ar`, `title_en`, `slug` (Unique)
- `excerpt_ar`, `excerpt_en`, `content_ar`, `content_en`
- `reading_time` (INTEGER, محسوب تلقائياً بناءً على عدد الكلمات)
- `medical_disclaimer_ar` (إخلاء مسؤولية طبي معتمد)
- `is_published`, `published_at`, `view_count`

---

### تطبيق المواعيد وحجوزات المرضى (appointments)
#### `appointments_patient`
- `id` (BigAutoField, PK)
- `full_name` (VARCHAR(200), Indexed)
- `phone_number` (VARCHAR(30), Indexed)
- `email` (EmailField, Nullable)
- `notes` (TEXT)
- `created_at`, `updated_at`

#### `appointments_appointment`
- `id` (BigAutoField, PK)
- `booking_id` (UUIDField, Unique, Indexed)
- `patient_id` (FK -> `appointments_patient.id`, ON DELETE PROTECT)  <!-- تم التحديث لمنع الحذف العرضي لبيانات وتاريخ المريض -->
- `branch_id` (FK -> `clinics_clinicbranch.id`, ON DELETE PROTECT)
- `service_id` (FK -> `services_medicalservice.id`, Nullable)
- `appointment_date` (DateField, Indexed)
- `appointment_time` (TimeField, Indexed)
- `status` (VARCHAR(20), Choices: `pending`, `confirmed`, `rejected`, `cancelled`, `completed`, `no_show`)
- `visit_reason` (VARCHAR(300)), `patient_notes` (TEXT), `staff_notes` (TEXT)
- **Database Constraints & Indexes (Phase 2 Hardening):**
  - **قيد فريد شرطي على مستوى PostgreSQL لمنع التعارض نهائياً:**
    `UniqueConstraint(fields=['branch', 'appointment_date', 'appointment_time'], condition=Q(status='confirmed'), name='unique_confirmed_appointment_per_branch_slot')`
  - `Index(['branch', 'appointment_date', 'status'])`
  - `Index(['appointment_date', 'appointment_time'])`

#### `appointments_appointmentstatushistory`
- `id` (BigAutoField, PK)
- `appointment_id` (FK -> `appointments_appointment.id`, ON DELETE CASCADE)
- `old_status`, `new_status`
- `changed_by_id` (FK -> `accounts_customuser.id`, Nullable)
- `notes` (TEXT), `timestamp` (DateTimeField)

---

## 3. آلية منع الحجز المزدوج وضمان تكامل المواعيد (Double Booking Prevention & Concurrency)

تعتمد خوارزمية الحجز وتأكيد المواعيد على دفاع ثلاثي الطبقات:
1. **التحقق من الفترات الشاغرة (Availability Layer):** قبل عرض أي موعد للمريض عبر واجهة `/api/slots/`، يتم استبعاد أي موعد مؤكد سابقاً لنفس الفرع والتاريخ والوقت، والتحقق الصارم من العطلات الأسبوعية والرسمية.
2. **التحقق السحابي عند الإنشاء (Service-Level Validation):** يتحقق `create_appointment_request` من عدم كون التاريخ والوقت في الماضي، وأن الفرع نشط، وأنه ليس عطلة رسمية أو أسبوعية، وأن الوقت داخل ساعات الدوام، وأنه لا يوجد موعد مؤكد مسبقاً.
3. **قفل السجلات المتزامنة (Row-Level Locking):** عند قيام موظف الاستقبال أو الطبيب بتأكيد موعد ما (`CONFIRMED`)، يتم استخدام `select_for_update()` داخل `transaction.atomic()` للتحقق من عدم وجود أي موعد مؤكد آخر في نفس التوقيت بدقة بالغة.
4. **الحماية الجدارية على مستوى قاعدة البيانات (PostgreSQL Constraint):** يمنع قيد `UniqueConstraint` الشرطي في PostgreSQL كتابة أو حفظ موعدين مؤكدين في نفس الفرع والتاريخ والوقت حتى لو تجاوز الطلب كافة حواجز الخادم في حالات التزامن القصوى (High Concurrency / Race Conditions).

