# دليل النشر والتشغيل في بيئة الإنتاج الحقيقية (Production Deployment Guide)
## عيادة الدكتور محمد أحمد الصياد - جراحة العظام والمفاصل الصناعية

---

## 1. المتطلبات المسبقة للخادم (Server Prerequisites)

* **نظام التشغيل الموصى به:** Ubuntu Server 22.04 LTS أو 24.04 LTS (أو Windows Server 2022/2025).
* **الحزم والخدمات المطلوبة:**
  - Python 3.12+ و pip و python3.12-venv
  - PostgreSQL 18
  - Nginx (كخادم ويب وكيل عكسي Reverse Proxy وموزع للملفات الثابتة)
  - Certbot (لإصدار شهادات SSL/TLS المجانية من Let's Encrypt)
  - Gunicorn (WSGI HTTP Server)

---

## 2. إعداد قاعدة بيانات الإنتاج (PostgreSQL Setup)

```sql
-- تسجيل الدخول كمستخدم postgres:
sudo -u postgres psql

-- إنشاء مستخدم وقاعدة بيانات الإنتاج المعزولة:
CREATE USER alsayyad_db_user WITH PASSWORD 'STRONG_RANDOMLY_GENERATED_PASSWORD_HERE';
CREATE DATABASE alsayyad_clinic_db OWNER alsayyad_db_user ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE alsayyad_clinic_db TO alsayyad_db_user;
\q
```

---

## 3. إعداد متغيرات بيئة الإنتاج (`.env.production`)

قم بإنشاء ملف `.env` في مجلد المشروع الرئيسي بالقيم الآمنة:

```ini
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=COMPLEX_CRYPTOGRAPHICALLY_RANDOM_KEY_AT_LEAST_64_CHARS_LONG
ALLOWED_HOSTS=alsayyad-clinic.ye,www.alsayyad-clinic.ye,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://alsayyad-clinic.ye,https://www.alsayyad-clinic.ye

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=alsayyad_clinic_db
DB_USER=alsayyad_db_user
DB_PASSWORD=STRONG_RANDOMLY_GENERATED_PASSWORD_HERE
DB_HOST=127.0.0.1
DB_PORT=5432
CONN_MAX_AGE=60

# Patient Data Cryptographic Key (Fernet 32-byte urlsafe base64)
# يمكن توليده عبر: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
PATIENT_DATA_ENCRYPTION_KEY=YOUR_GENERATED_32_BYTE_FERNET_KEY_HERE

# Security Headers
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Time & Locale
TIME_ZONE=Asia/Aden
LANGUAGE_CODE=ar

# Email (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=official@alsayyad-clinic.ye
EMAIL_HOST_PASSWORD=APP_SPECIFIC_PASSWORD_HERE
DEFAULT_FROM_EMAIL=عيادة الدكتور محمد الصياد <no-reply@alsayyad-clinic.ye>
SERVER_EMAIL=تنبيهات النظام <alerts@alsayyad-clinic.ye>
```

---

## 4. تجهيز مجلدات المشروع والأصول الثابتة

```bash
# 1. تفعيل البيئة الافتراضية وتثبيت المكتبات
cd /var/www/alsayyad_clinic
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. تطبيق ترحيلات قاعدة البيانات
python manage.py migrate --settings=config.settings.production

# 3. إنشاء جدول التخزين المؤقت المشترك (Multi-Worker Shared Cache)
python manage.py createcachetable clinic_system_cache --settings=config.settings.production

# 4. تجميع كافة الملفات الثابتة والأصول
python manage.py collectstatic --noinput --settings=config.settings.production

# 5. ضبط الصلاحيات للمستخدم www-data
sudo chown -R www-data:www-data /var/www/alsayyad_clinic/media
sudo chown -R www-data:www-data /var/www/alsayyad_clinic/logs
sudo chmod -R 750 /var/www/alsayyad_clinic/media
sudo chmod -R 750 /var/www/alsayyad_clinic/logs
```

---

## 5. إعداد خدمة Gunicorn عبر Systemd

أنشئ الملف `/etc/systemd/system/alsayyad_clinic.service`:

```ini
[Unit]
Description=Gunicorn Application Server for Dr. Mohammed Al-Sayyad Clinic
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/alsayyad_clinic
EnvironmentFile=/var/www/alsayyad_clinic/.env
ExecStart=/var/www/alsayyad_clinic/venv/bin/gunicorn \
          --config /var/www/alsayyad_clinic/gunicorn_config.py \
          config.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

تفعيل وتشغيل الخدمة:
```bash
sudo systemctl daemon-reload
sudo systemctl enable alsayyad_clinic
sudo systemctl start alsayyad_clinic
sudo systemctl status alsayyad_clinic
```

---

## 6. إعداد خادم Nginx وشهادة الأمان SSL

أنشئ إعدادات الموقع في `/etc/nginx/sites-available/alsayyad_clinic.conf`:

```nginx
upstream alsayyad_app_server {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name alsayyad-clinic.ye www.alsayyad-clinic.ye;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name alsayyad-clinic.ye www.alsayyad-clinic.ye;

    # شهادات Let's Encrypt SSL
    ssl_certificate /etc/letsencrypt/live/alsayyad-clinic.ye/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/alsayyad-clinic.ye/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # ترويسات الأمان
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # حجم الرفع الأقصى للصور
    client_max_body_size 10M;

    # الملفات الثابتة (Static Files)
    location /static/ {
        alias /var/www/alsayyad_clinic/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        access_log off;
    }

    # وسائط المستخدمين والصور المرفوعة (Media Files)
    location /media/ {
        alias /var/www/alsayyad_clinic/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
        # منع تنفيذ أي سكربتات بداخل مجلد الوسائط
        location ~* \.(php|pl|py|jsp|asp|sh|cgi)$ {
            deny all;
        }
    }

    # حظر الوصول للملفات الحساسة
    location ~ /\.(env|git|svn|hg) {
        deny all;
        return 404;
    }

    # تمرير الطلبات إلى تطبيق Gunicorn
    location / {
        proxy_pass http://alsayyad_app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
}
```

تفعيل الإعدادات وإصدار شهادة SSL:
```bash
sudo ln -s /etc/nginx/sites-available/alsayyad_clinic.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d alsayyad-clinic.ye -d www.alsayyad-clinic.ye
```

---

## 7. فحص الجاهزية النهائي عبر الطرفية (Final Verification)

```bash
# التأكد من فحص النشر لجانغو بنجاح تام
python manage.py check --deploy --settings=config.settings.production

# التحقق من استجابة خادم Gunicorn
curl -I https://alsayyad-clinic.ye/
```

