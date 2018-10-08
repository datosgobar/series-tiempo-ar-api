#! coding: utf-8
import logging
# noinspection PyUnresolvedReferences
from .base import *


INSTALLED_APPS += ("django_nose", )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# we don't want logging while running tests.
logging.disable(logging.CRITICAL)
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
DEBUG = False
TEMPLATE_DEBUG = False
TESTS_IN_PROGRESS = True

TEST_SERIES_NAME = 'test_series-{}'
TEST_SERIES_NAME_DELAYED = TEST_SERIES_NAME + '-delayed'

READ_DATAJSON_SHELL_CMD = 'mock_cmd'

RQ_QUEUES = {
    'default': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'high': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'low': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'scrapping': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'DEFAULT_TIMEOUT': 3600,
        'ASYNC': False,
    },
    'indexing': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
}

SENDFILE_BACKEND = 'sendfile.backends.development'
MINIO_STORAGE_MEDIA_BUCKET_NAME = 'tsapi.testing.media.bucket'
MINIO_STORAGE_ACCESS_KEY = "development"
MINIO_STORAGE_SECRET_KEY = "development"

DUMP_LOG_EXCEPTIONS = False