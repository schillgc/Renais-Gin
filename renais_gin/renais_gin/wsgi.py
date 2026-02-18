"""
WSGI config for renais_gin project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'renais_gin.settings')

# This application object is used by any WSGI server configured to use this file
application = get_wsgi_application()

# Apply WSGI middleware here if needed
# For example, for whitenoise in production:
# from whitenoise import WhiteNoise
# application = WhiteNoise(application)
