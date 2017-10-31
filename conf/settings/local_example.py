#! coding: utf-8
# noinspection PyUnresolvedReferences
from .base import *

ADMINS = (
    ('admin_name', 'admin_name@devartis.com'),
)

MANAGERS = ADMINS

# Default of docker container!
ES_URL = "http://elastic:changeme@localhost:9200/"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env('DATABASE_HOST'),
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
    }
}
