"""Settings for isolated automated tests.

These settings deliberately exclude the development toolbar and use only
Django's disposable test database. They must never be used for deployment.
"""

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

INSTALLED_APPS = [
    app for app in INSTALLED_APPS if app != "debug_toolbar"
]
MIDDLEWARE = [
    item for item in MIDDLEWARE
    if item != "debug_toolbar.middleware.DebugToolbarMiddleware"
]

STATICFILES_DIRS = [
    directory for directory in STATICFILES_DIRS if directory.is_dir()
]

CORS_ALLOW_ALL_ORIGINS = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
