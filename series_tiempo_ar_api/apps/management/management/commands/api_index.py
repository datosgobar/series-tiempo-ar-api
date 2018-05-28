#! coding: utf-8
import logging

from django.core.management import BaseCommand
from series_tiempo_ar_api.apps.management.tasks import schedule_api_indexing

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        schedule_api_indexing()
