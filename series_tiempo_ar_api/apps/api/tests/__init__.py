#! coding: utf-8
from django.conf import settings
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from .support.generate_data import get_generator
from .helpers import setup_database

elastic = ElasticInstance.get()


def setup():
    if not elastic.indices.exists(settings.TEST_INDEX):
        generator = get_generator()
        generator.run()
        setup_database()


def teardown():
    elastic.indices.delete(settings.TEST_INDEX)