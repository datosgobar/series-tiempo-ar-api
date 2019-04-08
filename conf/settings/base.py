#! coding: utf-8
from __future__ import absolute_import, unicode_literals

from os.path import dirname

import environ

from .api.api import *
from .api.metadata import *
from elasticsearch_dsl.connections import connections


SETTINGS_DIR = environ.Path(__file__) - 1
ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path(dirname(dirname(dirname(__file__))))

env = environ.Env()
environ.Env.read_env(SETTINGS_DIR('.env'))

connections.create_connection(hosts=env("ES_URLS", default=DEFAULT_ES_URL).split(","),
                              timeout=30)

DEBUG = True

ADMINS = ()

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-ar'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = str(APPS_DIR('media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/series/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/series/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    str(ROOT_DIR.path('series_tiempo_ar_api/static')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9!n$10$pksr3j5dv*4bc21ke$%0$zs18+vse=al8dpfzi_9w4y'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
)

ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'series_tiempo_ar_api.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'conf.wsgi.application'


def export_vars(_):
    data = {
        'API_VERSION': env('API_VERSION', default='local')
    }
    return data


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'conf.settings.base.export_vars',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'debug': True
        },
    },
]

DJANGO_BASE_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)

VENDOR_APPS = (
    "django_rq",
    'sendfile',
    'des',
    'scheduler',
    'django_datajsonar',
    'solo',
    'minio_storage',
    'admin_reorder',
)

APPS = (
    'series_tiempo_ar_api.apps.api.apps.ApiConfig',
    'series_tiempo_ar_api.apps.analytics',
    'series_tiempo_ar_api.apps.management.apps.ManagementConfig',
    'series_tiempo_ar_api.apps.metadata.apps.MetadataConfig',
    'series_tiempo_ar_api.apps.dump',
    'series_tiempo_ar_api.libs.indexing',
    'series_tiempo_ar_api.libs.custom_admins',
)

INSTALLED_APPS = DJANGO_BASE_APPS + VENDOR_APPS + APPS

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        "rq_console": {
            "level": "DEBUG",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
        'apps': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'filters': ['require_debug_true'],
            "formatter": "simple",
        },
        'production': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'filters': ['require_debug_false'],
            "formatter": "verbose",
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'series_tiempo_ar_api': {
            'handlers': ['apps', 'production'],
            'level': 'INFO',
            'propagate': False,
        },
        "rq.worker": {
            "handlers": ["rq_console", ],
            "level": "DEBUG"
        },
    }
}

# EMAILS
EMAIL_BACKEND = 'des.backends.ConfiguredEmailBackend'


DEFAULT_REDIS_HOST = env("DEFAULT_REDIS_HOST", default="localhost")
DEFAULT_REDIS_PORT = env("DEFAULT_REDIS_PORT", default="6379")
DEFAULT_REDIS_DB = env("DEFAULT_REDIS_DB", default="0")

REDIS_SETTINGS = {
    'HOST': DEFAULT_REDIS_HOST,
    'PORT': DEFAULT_REDIS_PORT,
    'DB': DEFAULT_REDIS_DB,
}

# Colas de Redis. Existe una por tarea asincrónica a ejecutar.
RQ_QUEUE_NAMES = [
    'default',
    'upkeep',
    'dj_indexing',
    'indexing',
    'meta_indexing',
    'csv_dump',
    'xlsx_dump',
    'sql_dump',
    'dta_dump',
    'analytics',
    'integration_test',
    'api_index',
    'api_report',
    'analytics',
    'hits_indicators',
]
RQ_QUEUES = {name: REDIS_SETTINGS for name in RQ_QUEUE_NAMES}

ENV_TYPE = env('ENV_TYPE', default='')

# Tarea a ser croneada para indexación. Defaults para uso local, en producción se deben setear estas variables!
IMPORT_ANALYTICS_SCRIPT_PATH = env('IMPORT_ANALYTICS_CMD_PATH', default='/bin/true import_analytics')
INDEX_METADATA_SCRIPT_PATH = env('INDEX_METADATA_CMD_PATH', default='/bin/true index_metadata')
INTEGRATION_TEST_SCRIPT_PATH = env('INTEGRATION_TEST_CMD_PATH', default='/bin/true integration_test')

# Config de Django-datajsonar
DATAJSON_AR_TIME_SERIES_ONLY = True
DATAJSON_AR_DISTRIBUTION_STORAGE = 'minio_storage.storage.MinioMediaStorage'

# Minio: File system distribuido, usado para correr tareas que generan archivos en un ambiente, y leerlos
# desde el web server
MINIO_STORAGE_ENDPOINT = env('MINIO_STORAGE_ENDPOINT', default="localhost:9000")
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = env('MINIO_STORAGE_BUCKET_NAME', default='tsapi.dev.media.bucket')
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True

# Stages asincrónicos a ejecutar con el Synchronizer de Django-datajsonar
DATAJSONAR_STAGES = {
    'Read Datajson (corrida completa)': {
        'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
    'Read Datajson (sólo metadatos)': {
        'callable_str': 'django_datajsonar.tasks.schedule_metadata_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
    'Indexación de datos (sólo actualizados)': {
        'callable_str': 'series_tiempo_ar_api.apps.management.tasks.indexation.schedule_api_indexing',
        'queue': 'api_index',
        'task': 'series_tiempo_ar_api.apps.management.models.IndexDataTask',
    },
    'Indexación de datos (forzar indexación)': {
        'callable_str': 'series_tiempo_ar_api.apps.management.tasks.indexation.schedule_force_api_indexing',
        'queue': 'api_index',
        'task': 'series_tiempo_ar_api.apps.management.models.IndexDataTask',
    },
    'Generación de dumps CSV': {
        'callable_str': 'series_tiempo_ar_api.apps.dump.tasks.enqueue_write_csv_task',
        'queue': 'csv_dump',
        'task': 'series_tiempo_ar_api.apps.dump.models.GenerateDumpTask',
    },
    'Generación de dumps XLSX': {
        'callable_str': 'series_tiempo_ar_api.apps.dump.tasks.enqueue_write_xlsx_task',
        'queue': 'xlsx_dump',
        'task': 'series_tiempo_ar_api.apps.dump.models.GenerateDumpTask',
    },
    'Generación de dumps SQL': {
        'callable_str': 'series_tiempo_ar_api.apps.dump.tasks.enqueue_write_sql_task',
        'queue': 'sql_dump',
        'task': 'series_tiempo_ar_api.apps.dump.models.GenerateDumpTask',
    },
    'Generación de dumps DTA': {
        'callable_str': 'series_tiempo_ar_api.apps.dump.tasks.enqueue_write_dta_task',
        'queue': 'dta_dump',
        'task': 'series_tiempo_ar_api.apps.dump.models.GenerateDumpTask',
    },
    'Indexación de metadatos': {
        'callable_str': 'series_tiempo_ar_api.apps.metadata.indexer.metadata_indexer.enqueue_new_index_metadata_task',
        'queue': 'meta_indexing',
        'task': 'series_tiempo_ar_api.apps.metadata.models.IndexMetadataTask',
    },
    'Test de integración': {
        'callable_str': 'series_tiempo_ar_api.apps.management.tasks.integration_test.enqueue_new_integration_test',
        'queue': 'integration_test',
        'task': 'series_tiempo_ar_api.apps.management.models.IntegrationTestTask',
    },
    'Reporte de indexación': {
        'callable_str': 'series_tiempo_ar_api.libs.indexing.tasks.send_indexation_report_email',
        'queue': 'api_report',
        'task': 'series_tiempo_ar_api.apps.management.models.IndexDataTask',
    },
    'Importado de analytics': {
        'callable_str': 'series_tiempo_ar_api.apps.analytics.tasks.enqueue_new_import_analytics_task',
        'queue': 'analytics',
    },
    'Cálculo de indicadores de popularidad': {
        'callable_str': 'series_tiempo_ar_api.apps.analytics.tasks.enqueue_new_calculate_hits_indicators_task',
        'queue': 'hits_indicators'
    },
}

ADMIN_REORDER = (
    'auth',
    'django_datajsonar',
    'management',
    'metadata',
    'dump',
    'analytics',
    {'app': 'des', 'label': 'Configuración correo'},
    'scheduler',
    'sites',
)
