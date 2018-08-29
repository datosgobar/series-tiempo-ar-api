#! coding: utf-8
# noinspection PyUnresolvedReferences
from .base import *

ADMINS = (
    ('admin_name', 'admin_name@devartis.com'),
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

SENDFILE_BACKEND = 'sendfile.backends.development'

for queue in RQ_QUEUES.values():
    queue['ASYNC'] = False

DATAJSON_AR_DISTRIBUTION_STORAGE = 'minio_storage.storage.MinioMediaStorage'
MINIO_STORAGE_ACCESS_KEY = env('MINIO_ACCESS_KEY')
MINIO_STORAGE_SECRET_KEY = env('MINIO_SECRET_KEY')
