# دليل تشغيل ونشر بيئة التدقيق والتجربة الميدانية (Staging Deployment Guide)
## عيادة الدكتور محمد أحمد الصياد - جراحة العظام والمفاصل الصناعية

---

## 1. نظرة عامة على بيئة Staging

تم تصميم بيئة التدقيق والتجربة (Staging Environment) لتكون **نسخة متطابقة تماماً مع بيئة الإنتاج الحقيقية**، ولكنها معزولة بشكل صارم:
- **قاعدة بيانات منفصلة:** `alsayyad_clinic_staging_db` (لا تحتوي على أي بيانات مرضى حقيقيين).
- **إيقاف وضع التطوير:** `DEBUG = False`.
- **مخزن وسائط مستقل:** `media_staging/`.
- **نظام تخزين مؤقت مشترك متعدد العمليات:** Multi-Worker Database Cache على جدول `clinic_system_cache`.
- **ملف إعدادات مخصص:** [`config/settings/staging.py`](file:///d:/DR.MOHAMMED%20ALSAYYAD/config/settings/staging.py).
- **متغيرات بيئة خاصة:** [`.env.staging`](file:///d:/DR.MOHAMMED%20ALSAYYAD/.env.staging).

---

## 2. متطلبات التشغيل

1. **Python 3.12+**
2. **PostgreSQL 18** (شغال على المنفذ `5432`)
3. تثبيت المكتبات المحدثة:
   ```bash
   pip install -r requirements.txt
   ```

---

## 3. خطوات تهيئة وتشغيل بيئة Staging خطوة بخطوة

### الخطوة 1: التحقق من وجود قاعدة بيانات Staging
```sql
-- من خلال عميل PostgreSQL (psql):
CREATE DATABASE alsayyad_clinic_staging_db ENCODING 'UTF8';
```

### الخطوة 2: تطبيق ترحيلات الجداول والقيود
```bash
python manage.py migrate --settings=config.settings.staging
```

### الخطوة 3: إنشاء جدول التخزين المؤقت المشترك (Multi-Worker Shared Cache)
```bash
python manage.py createcachetable clinic_system_cache --settings=config.settings.staging
```

### الخطوة 4: تصفير وزراعة البيانات التجريبية النظيفة (Staging Reset)
يقوم هذا الأمر بتجهيز كامل حسابات الأدوار الأربعة (مشرف، طبيب، استقبال، محرر محتوى) وحالات المواعيد التجريبية:
```bash
python manage.py reset_staging_data --settings=config.settings.staging
```

---

## 4. بيانات الاعتماد لحسابات Staging التجريبية

> **تنبيه:** تم سحب كلمات المرور من ملف `.env.staging` لضمان عدم وجود بيانات اعتماد ثابتة مكشوفة في الأكواد.

| الحساب | الدور (Role) | اسم المستخدم | كلمة المرور الأولية للـ Staging | الصلاحيات الأساسية |
| :--- | :--- | :--- | :--- | :--- |
| **المشرف العام** | Super Administrator | `admin_staging` | تُضبط عبر `ADMIN_INITIAL_PASSWORD` | كامل إعدادات النظام، الفروع، السجلات الرقابية، الحسابات |
| **الطبيب** | Doctor | `doctor_staging` | تُضبط عبر `DOCTOR_INITIAL_PASSWORD` | جدول المواعيد السريرية، الملف المهني، الخدمات، المقالات |
| **موظف الاستقبال** | Receptionist | `reception_staging` | تُضبط عبر `RECEPTION_INITIAL_PASSWORD` | إدارة طلبات الحجز، تقويم المواعيد، تأكيد وإلغاء الزيارات |
| **مدير المحتوى** | Content Manager | `content_staging` | تُضبط عبر `CONTENT_INITIAL_PASSWORD` | المقالات الطبية، السلاسل التثقيفية، فيديوهات YouTube |

---

## 5. تشغيل خادم Staging للتحقق المحلي

```bash
python manage.py runserver 127.0.0.1:8000 --settings=config.settings.staging
```

روابط الفحص:
- **الموقع العام:** `http://127.0.0.1:8000/`
- **حجز موعد جديد:** `http://127.0.0.1:8000/booking/`
- **الاستعلام الآمن عن الموعد:** `http://127.0.0.1:8000/booking/status/`
- **لوحة التحكم الإدارية:** `http://127.0.0.1:8000/dashboard/`

---

## 6. إجراءات إعادة تصفير بيانات Staging بعد انتهاء جلسات الاختبار

عند رغبة فريق العيادة في إعادة بدء دورة اختبار جديدة ببيانات نظيفة، يكفي تشغيل أمر واحد:
```bash
python manage.py reset_staging_data --settings=config.settings.staging
```
يحظر هذا الأمر تلقائياً العمل على قاعدة البيانات الإنتاجية لحماية السجلات الحقيقية.

