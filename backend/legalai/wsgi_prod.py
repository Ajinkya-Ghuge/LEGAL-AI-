"""
WSGI config for LegalAI production deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legalai.settings_prod')

application = get_wsgi_application()
