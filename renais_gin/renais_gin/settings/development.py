"""
Development-specific settings for Renais Gin.
"""

from .base import *

# Debug settings
DEBUG = True

# Additional apps for development
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Additional middleware for development
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Django extensions configuration
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True

# Email configuration for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable SSL redirect in development
SECURE_SSL_REDIRECT = False

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Logging configuration for development
LOGGING['loggers']['core']['level'] = 'DEBUG'
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Development-specific Renais settings
RENAIS_SETTINGS.update({
    'BLOCKCHAIN_MOCK_MODE': True,
    'AI_VALIDATION_THRESHOLD': 0.5,  # Lower threshold for testing
})

print("Development settings loaded - Debug mode is ON")
