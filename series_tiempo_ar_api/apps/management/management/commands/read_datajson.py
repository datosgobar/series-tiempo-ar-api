#! coding: utf-8
from django.core.management import BaseCommand

from series_tiempo_ar_api.apps.management.models import ReadDataJsonTask
from series_tiempo_ar_api.apps.management.tasks import read_datajson


class Command(BaseCommand):
    """Comando para ejecutar la indexación manualmente de manera sincrónica,
    útil para debugging"""
    def handle(self, *args, **options):
        task = ReadDataJsonTask()
        task.save()
        read_datajson(task, async=False)
