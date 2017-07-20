#! coding: utf-8
# noinspection PyUnresolvedReferences
from .base import *

ADMINS = (
    ('admin_name', 'admin_name@devartis.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': env("DATABASE_NAME"),
    }
}
