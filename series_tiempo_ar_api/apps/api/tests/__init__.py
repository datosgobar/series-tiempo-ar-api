#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl.connections import connections

from .helpers import setup_database
from .support.generate_data import get_generator

elastic = connections.get_connection()


def setup():
    if not elastic.indices.exists(settings.TEST_INDEX):
        generator = get_generator()
        generator.run()
        setup_database()


def teardown():
    elastic.indices.delete(settings.TEST_INDEX)
