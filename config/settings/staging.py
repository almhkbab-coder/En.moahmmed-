import os
from .base import *

# ==========================================
# STAGING ENVIRONMENT CONFIGURATION (PHASE 3)
# ==========================================
DEBUG = False

if os.getenv('RENDER'):
    if not os.getenv('SECRET_KEY'):
        import secrets
        SECRET_KEY = secrets.token_urlsafe(64)

# Enable public forms (booking & contact) by default on staging
PUBLIC_FORMS_ENABLED = os.getenv('PUBLIC_FORMS_ENABLED', 'True').lower() in ('true', '1', 'yes')

# Staging Allowed Hosts
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv(
        'STAGING_ALLOWED_HOSTS',
        'staging.alsayyad-clinic.ye,localhost,127.0.0.1,testserver'
    ).split(',') if host.strip()
]

# Dedicated Staging Database (Completely isolated from Production)
STAGING_DB_NAME = os.getenv('STAGING_DB_NAME', 'alsayyad_clinic_staging_db')
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=60,
        ssl_require=True,
    )
else:
    DATABASES['default']['NAME'] = STAGING_DB_NAME
    DATABASES['default']['CONN_MAX_AGE'] = 60

RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']
else:
    CSRF_TRUSTED_ORIGINS = []

# Multi-Worker Shared Cache Backend (Database-backed or Redis)
REDIS_URL = os.getenv('REDIS_URL')
if os.getenv('STAGING_CACHE_BACKEND') == 'locmem':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'clinic_staging',
        }
    }
elif REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'clinic_staging',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'clinic_system_cache',
            'TIMEOUT': 900,
            'OPTIONS': {
                'MAX_ENTRIES': 5000,
            }
        }
    }

# Staging Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = os.getenv('STAGING_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_SECURE = os.getenv('STAGING_COOKIE_SECURE', 'False') == 'True'
SECURE_SSL_REDIRECT = os.getenv('STAGING_SSL_REDIRECT', 'False') == 'True'
if os.getenv('RENDER'):
    CSRF_COOKIE_SECURE = os.getenv('STAGING_COOKIE_SECURE', 'True') == 'True'
    SESSION_COOKIE_SECURE = os.getenv('STAGING_COOKIE_SECURE', 'True') == 'True'
    SECURE_SSL_REDIRECT = os.getenv('STAGING_SSL_REDIRECT', 'True') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Dedicated Staging Media Directory (Isolates test uploads from production)
MEDIA_ROOT = BASE_DIR / 'media_staging'

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Privacy-Respecting Staging Logging (No patient health info in logs)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'staging_fmt': {
            'format': '[{asctime}] {levelname} [{process}:{thread}] {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'staging_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'staging.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'staging_fmt',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'staging_fmt',
        },
    },
    'root': {
        'handlers': ['console', 'staging_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django.security': {
            'handlers': ['staging_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

