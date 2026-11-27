"""
Django settings for renais_gin project.
"""

from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    """Parse boolean environment values without treating arbitrary text as true."""
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(f"{name} must be a boolean value")


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY or not SECRET_KEY.strip():
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be set to a non-empty value."
    )
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be at least 50 characters and contain at least 5 distinct characters."
    )

DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
elif not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS must list the production hostnames when DEBUG is false."
    )


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'renais_gin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'renais_gin.wsgi.application'

DB_ENGINE = os.environ.get("DJANGO_DB_ENGINE", "sqlite").strip().lower() or "sqlite"
if DB_ENGINE == "sqlite":
    if not DEBUG:
        raise ImproperlyConfigured(
            "DJANGO_DB_ENGINE=postgresql (or postgres) is required when DJANGO_DEBUG is false."
        )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.environ.get("DJANGO_DB_NAME") or BASE_DIR / "db.sqlite3",
        }
    }
elif DB_ENGINE in {"postgres", "postgresql"}:
    required_db_values = (
        "DJANGO_DB_NAME",
        "DJANGO_DB_USER",
        "DJANGO_DB_PASSWORD",
        "DJANGO_DB_HOST",
    )
    missing_db_values = [
        name for name in required_db_values if not os.environ.get(name, "").strip()
    ]
    if missing_db_values:
        raise ImproperlyConfigured(
            "PostgreSQL requires these environment variables: "
            + ", ".join(missing_db_values)
        )

    raw_db_port = os.environ.get("DJANGO_DB_PORT", "5432").strip() or "5432"
    try:
        db_port = int(raw_db_port)
    except ValueError as exc:
        raise ImproperlyConfigured(
            "DJANGO_DB_PORT must be an integer between 1 and 65535."
        ) from exc
    if not 1 <= db_port <= 65_535:
        raise ImproperlyConfigured(
            "DJANGO_DB_PORT must be an integer between 1 and 65535."
        )

    db_sslmode = (
        os.environ.get("DJANGO_DB_SSLMODE", "verify-full").strip().lower()
        or "verify-full"
    )
    if db_sslmode not in {"verify-ca", "verify-full"}:
        raise ImproperlyConfigured(
            "DJANGO_DB_SSLMODE must verify the server certificate "
            "(verify-ca or verify-full)."
        )

    raw_conn_max_age = (
        os.environ.get("DJANGO_DB_CONN_MAX_AGE", "60").strip() or "60"
    )
    try:
        conn_max_age = int(raw_conn_max_age)
    except ValueError as exc:
        raise ImproperlyConfigured(
            "DJANGO_DB_CONN_MAX_AGE must be an integer between 0 and 3600."
        ) from exc
    if not 0 <= conn_max_age <= 3_600:
        raise ImproperlyConfigured(
            "DJANGO_DB_CONN_MAX_AGE must be an integer between 0 and 3600."
        )

    db_options = {"sslmode": db_sslmode}
    db_sslrootcert = os.environ.get("DJANGO_DB_SSLROOTCERT", "").strip()
    if db_sslrootcert:
        db_options["sslrootcert"] = db_sslrootcert

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DJANGO_DB_NAME"].strip(),
            "USER": os.environ["DJANGO_DB_USER"].strip(),
            "PASSWORD": os.environ["DJANGO_DB_PASSWORD"],
            "HOST": os.environ["DJANGO_DB_HOST"].strip(),
            "PORT": str(db_port),
            "CONN_MAX_AGE": conn_max_age,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": db_options,
        }
    }
else:
    raise ImproperlyConfigured("DJANGO_DB_ENGINE must be sqlite or postgresql.")

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Kentucky/Louisville'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [static_dir] if static_dir.is_dir() else []
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Enable HSTS only after the production domain and every covered subdomain
# are verified to serve HTTPS. Do not opt into browser preload by default.
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_HSTS_PRELOAD", False)

# Trust forwarded HTTPS only when the configured reverse proxy controls this header.
if env_bool("DJANGO_TRUST_PROXY", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

PDF_UPLOAD_PATH = 'pdfs/user_uploads/'
PDF_REPORT_PATH = 'pdfs/generated_reports/'
