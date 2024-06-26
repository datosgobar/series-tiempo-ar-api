#! coding: utf-8
import os
import raven
# noinspection PyUnresolvedReferences
from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

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
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    'environment': env("SENTRY_ENVIRONMENT", default=""),
}

INSTALLED_APPS += 'raven.contrib.django.raven_compat',

MINIO_STORAGE_ACCESS_KEY = env('MINIO_ACCESS_KEY')
MINIO_STORAGE_SECRET_KEY = env('MINIO_SECRET_KEY')


MINIO_SERVE_FILES_URL = '/series/files/'

IMPORT_ANALYTICS_SCRIPT_PATH = env('IMPORT_ANALYTICS_CMD_PATH')
INDEX_METADATA_SCRIPT_PATH = env('INDEX_METADATA_CMD_PATH')

CORS_ORIGIN_ALLOW_ALL = True
