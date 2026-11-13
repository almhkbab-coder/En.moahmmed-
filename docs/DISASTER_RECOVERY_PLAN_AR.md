# خطة التعافي من الكوارث واستمرارية الأعمال الطبية (Disaster Recovery Plan)
## عيادة الدكتور محمد أحمد الصياد - جراحة العظام والمفاصل الصناعية

---

## 1. أهداف التعافي ومؤشرات الخدمة (Recovery Objectives)

* **الهدف الزمني لنقطة الاستعادة (RPO - Recovery Point Objective):**  
  أقل من **24 ساعة** (نسخ احتياطي يومي آلي مجدول في تمام الساعة 2:00 فجراً)، مع إمكانية خفضها لساعات عبر أرشفة سجلات PostgreSQL WAL.
* **الهدف الزمني لفترة التعافي (RTO - Recovery Time Objective):**  
  أقل من **30 دقيقة** لاستعادة قاعدة البيانات وتفعيل الخدمة بالكامل في حال انهيار الخادم الرئيسي.

---

## 2. عناصر النسخ الاحتياطي الثلاثية (Backup Components)

يتكون نظام العيادة من ثلاثة عناصر أساسية لا تكتمل خطة الاستعادة إلا بوجودها جميعاً:

```
┌─────────────────────────────────────────────────────────────┐
│                حزمة النسخ الاحتياطي للعيادة                │
├──────────────────────────────┬──────────────────────────────┤
│ 1. قاعدة بيانات PostgreSQL   │ جداول المواعيد، المرضى المشفرة│
│ 2. مجلد الوسائط (media/)     │ صور الأشعة، صور الخدمات      │
│ 3. مفتاح التشفير البيئي      │ PATIENT_DATA_ENCRYPTION_KEY │
└──────────────────────────────┴──────────────────────────────┘
```

> [!CAUTION]
> **قاعدة أمنية حرجة:**  
> **يحظر تماماً** حفظ مفتاح التشفير `PATIENT_DATA_ENCRYPTION_KEY` بجانب ملف النسخة الاحتياطية للقاعدة في نفس الخادم؛ ففي حال تم اختراق الخادم سيتمكن المهاجم من فك تشفير الأسماء. يجب تخزين المفتاح في خزنة كلمات مرور مشفرة خارجية ومحمية بالتحقق الثنائي (2FA).

---

## 3. آلية النسخ الاحتياطي اليومي المؤتمت (Automated Daily Backup Procedure)

### 3.1 أمر استخراج قاعدة البيانات (PostgreSQL Dump Script)
يتم تشغيل هذا السكربت يومياً في تمام الساعة 02:00 فجراً عبر مهام الجدولة (Cron Job / Windows Task Scheduler):

```bash
#!/bin/bash
set -e

# تحديد المتغيرات
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/clinic/database"
MEDIA_DIR="/var/www/alsayyad_clinic/media"
MEDIA_BACKUP_DIR="/var/backups/clinic/media"
DB_NAME="alsayyad_clinic_db"
DB_USER="postgres"

mkdir -p "$BACKUP_DIR"
mkdir -p "$MEDIA_BACKUP_DIR"

# 1. نسخ قاعدة بيانات PostgreSQL بصيغة مخصصة مضغوطة مفهرسة (-Fc)
export PGPASSWORD="$DB_PASSWORD"
pg_dump -U "$DB_USER" -h 127.0.0.1 -p 5432 -Fc "$DB_NAME" > "$BACKUP_DIR/clinic_db_$TIMESTAMP.dump"

# 2. أرشفة مجلد الوسائط والصور المرفوعة
tar -czf "$MEDIA_BACKUP_DIR/media_$TIMESTAMP.tar.gz" -C "$MEDIA_DIR" .

# 3. مزامنة النسخ إلى خادم تخزين خارجي معزول (Off-site Storage / S3 / rsync)
# rsync -avz -e ssh "$BACKUP_DIR/clinic_db_$TIMESTAMP.dump" backup_server:/remote_backups/clinic/

# 4. تطبيق سياسة الحفظ والتنظيف (Retention Policy)
# الاحتفاظ بآخر 30 يوماً من النسخ اليومية وحذف الأقدم
find "$BACKUP_DIR" -name "clinic_db_*.dump" -mtime +30 -exec rm -f {} \;
find "$MEDIA_BACKUP_DIR" -name "media_*.tar.gz" -mtime +30 -exec rm -f {} \;

echo "[$(date)] Backup completed successfully: clinic_db_$TIMESTAMP.dump"
```

---

## 4. سياسة الاحتفاظ بالنسخ الاحتياطية (Retention Policy)

* **النسخ اليومية (Daily Backups):** الاحتفاظ بنسخة لكل يوم لآخر **30 يوماً**.
* **النسخ الأسبوعية (Weekly Backups):** الاحتفاظ بنسخة نهاية كل أسبوع لآخر **12 أسبوعاً**.
* **النسخ الشهرية (Monthly Backups):** الاحتفاظ بنسخة أول كل شهر لآخر **24 شهراً** للأرشفة الطبية والقانونية.

---

## 5. دليل إجراءات الاستعادة والتعافي خطوة بخطوة (Restoration Runbook)

في حال حدوث تلف في البيانات أو تعطل في الخادم، يتم اتباع الخطوات التالية بدقة:

### الخطوة 1: تهيئة البيئة وتجهيز مفتاح التشفير
تأكد من إدراج مفتاح التشفير البيئي في ملف التكوين السحابي:
```bash
export PATIENT_DATA_ENCRYPTION_KEY="قيمة_المفتاح_المسترجعة_من_الخزنة_المحمية"
```

### الخطوة 2: إنشاء قاعدة بيانات نظيفة
```bash
# تسجيل الدخول كمسؤول PostgreSQL
psql -U postgres -h 127.0.0.1 -c "CREATE DATABASE alsayyad_clinic_db ENCODING 'UTF8';"
```

### الخطوة 3: استعادة قاعدة البيانات عبر pg_restore
```bash
pg_restore -U postgres -h 127.0.0.1 -d alsayyad_clinic_db --clean --if-exists /path/to/backup/clinic_db_YYYYMMDD_HHMMSS.dump
```

### الخطوة 4: استعادة ملفات الوسائط والصور المرفوعة
```bash
tar -xzf /path/to/backup/media_YYYYMMDD_HHMMSS.tar.gz -C /var/www/alsayyad_clinic/media/
```

### الخطوة 5: تطبيق ترحيلات التوافق (إن وجدت ترحيلات أحدث)
```bash
python manage.py migrate --settings=config.settings.production
```

### الخطوة 6: إنشاء جدول التخزين المؤقت المشترك (Cache Table)
```bash
python manage.py createcachetable clinic_system_cache --settings=config.settings.production
```

---

## 6. قائمة التحقق بعد الاستعادة (Post-Restore Verification Checklist)

قبل فتح المنظومة لطاقم العيادة، يجب التحقق من النقاط التالية:

- [ ] نجاح الاتصال بقاعدة البيانات واكتمال فحص جانغو `python manage.py check --settings=config.settings.production`.
- [ ] فحص سجلات المرضى والتأكد من فك تشفير الأسماء بنجاح باستخدام مفتاح التشفير المستعاد.
- [ ] فحص جدول المواعيد والتأكد من ظهور حجوزات اليوم والأيام القادمة وحالاتها وسجل التعديلات.
- [ ] فحص ملف الطبيب الرسمي والخدمات الطبية والتأكد من ظهورها في الواجهة.
- [ ] تجربة تسجيل دخول المشرف وموظف الاستقبال والتأكد من صحة الصلاحيات.
- [ ] التأكد من ظهور الصور والشعارات المرفوعة في الواجهة العامة.

