#! coding: utf-8
from django.conf import settings

from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from .helpers import setup_database
from .support.generate_data import get_generator

elastic = ElasticInstance.get()


def setup():
    if not elastic.indices.exists(settings.TEST_INDEX):
        generator = get_generator()
        generator.run()
        setup_database()


def teardown():
    elastic.indices.delete(settings.TEST_INDEX)