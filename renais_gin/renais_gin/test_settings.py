"""Isolated settings for fast in-memory domain tests."""
from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
MEDIA_ROOT = "/tmp/renais-gin-functional-tests-media"
STATIC_ROOT = "/tmp/renais-gin-functional-tests-static"
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
