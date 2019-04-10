#! coding: utf-8
import logging

from django.core.management import BaseCommand
from series_tiempo_ar_api.apps.management.tasks.indexation import schedule_api_indexing

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--force', default=False, action='store_true')

    def handle(self, *args, **options):
        force = options['force']
        schedule_api_indexing(force=force)
