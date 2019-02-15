#! coding: utf-8
from django.core.management import BaseCommand
from django_rq import job

from series_tiempo_ar_api.apps.analytics.elasticsearch.index import AnalyticsIndexer
from series_tiempo_ar_api.apps.analytics.models import Query
from series_tiempo_ar_api.apps.analytics.tasks import enqueue_new_import_analytics_task


class Command(BaseCommand):
    def handle(self, *args, **options):
        index_analytics.delay()
        self.stdout.write("Indexación de queries a ES comenzada")


@job('default', timeout=-1)
def index_analytics():
    queryset = Query.objects.all()
    AnalyticsIndexer().index(queryset)
