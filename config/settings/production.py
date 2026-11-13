import os
from .base import *

# ==============================================================
# AL-SAYYAD CLINIC — PRODUCTION CONFIGURATION (PHASE 4 AUDIT)
# ==============================================================
DEBUG = False

# Production Allowed Hosts & CSRF Origins
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv(
        'ALLOWED_HOSTS',
        'alsayyad-clinic.ye,www.alsayyad-clinic.ye,127.0.0.1'
    ).split(',') if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'https://alsayyad-clinic.ye,https://www.alsayyad-clinic.ye'
    ).split(',') if o.strip()
]

# Production Database Settings
DATABASES['default']['NAME'] = os.getenv('DB_NAME', 'alsayyad_clinic_db')
DATABASES['default']['CONN_MAX_AGE'] = int(os.getenv('CONN_MAX_AGE', 60))

# Multi-Worker Shared Cache (Redis or PostgreSQL DatabaseCache)
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'clinic_prod',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'clinic_system_cache',
            'TIMEOUT': 900,
            'OPTIONS': {
                'MAX_ENTRIES': 10000,
            }
        }
    }

# HTTPS & Web Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', 31536000))  # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static and Media Storage
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# SMTP Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@alsayyad-clinic.ye')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'alerts@alsayyad-clinic.ye')

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Privacy-Preserving Production Logging (Zero Patient Data Exposure)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'prod_verbose': {
            'format': '[{asctime}] {levelname} [{process}:{thread}] {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'prod_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'production.log',
            'maxBytes': 20 * 1024 * 1024,  # 20 MB
            'backupCount': 10,
            'formatter': 'prod_verbose',
            'encoding': 'utf-8',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 20 * 1024 * 1024,  # 20 MB
            'backupCount': 10,
            'formatter': 'prod_verbose',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'prod_verbose',
        },
    },
    'root': {
        'handlers': ['console', 'prod_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['prod_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
