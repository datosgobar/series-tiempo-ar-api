#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl.connections import connections

from .helpers import setup_database
from .support.generate_data import get_generator

elastic = connections.get_connection()


def setup():
    setup_database()
    if not elastic.indices.exists(settings.TS_INDEX):
        generator = get_generator()
        generator.run()


def teardown():
    if elastic.indices.exists(settings.TS_INDEX):
        elastic.indices.delete(settings.TS_INDEX)
