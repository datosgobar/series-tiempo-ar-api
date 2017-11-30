#! coding: utf-8
import os
import raven
# noinspection PyUnresolvedReferences
from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Admin name', 'admin_name@devartis.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env('DATABASE_HOST'),
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
    }
}

MEDIA_ROOT = env('MEDIA_ROOT')
STATIC_ROOT = env('STATIC_ROOT')
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

RAVEN_CONFIG = {
    'dsn': env('RAVEN_DSN', default=""),
   # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

INSTALLED_APPS += 'raven.contrib.django.raven_compat',

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default="")
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default="")
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default="")
EMAIL_USE_TLS = True
