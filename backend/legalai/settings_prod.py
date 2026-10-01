"""
Production settings for LegalAI on Render + Supabase
"""
import os
import dj_database_url
from .settings import *

# SECURITY
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# ALLOWED_HOSTS - Support both Render and custom domain
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = []

# Add Render and custom domains
ALLOWED_HOSTS.extend([
    '.onrender.com',      # nexuslaw1.onrender.com
    'legalx.me',          # legalx.me
    'www.legalx.me',      # www.legalx.me
])

# Remove duplicates while preserving order
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

# CSRF - Trust both Render and custom domain origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://legalx.me',
    'https://www.legalx.me',
]

# DATABASE - Supabase PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MIDDLEWARE - Add WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# GEMINI API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# CORS - Allow custom domain
CORS_ALLOWED_ORIGINS = [
    'https://legalx.me',
    'https://www.legalx.me',
    'https://nexuslaw1.onrender.com',
]
CORS_ALLOW_CREDENTIALS = True

# MEDIA FILES (if using file uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
