#! coding: utf-8
from django.conf import settings
from django.core.management import call_command
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance

elastic = ElasticInstance.get()

if not elastic.indices.exists(settings.TEST_INDEX):
    call_command('generate_data')
