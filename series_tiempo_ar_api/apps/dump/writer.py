import logging

from traceback import format_exc

from django.utils import timezone
from django.conf import settings
from django_rq import get_queue
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump import constants
from .models import GenerateDumpTask, DumpFile

logger = logging.Logger(__name__)


class Writer:

    def __init__(self, dump_type: str, action: callable, recursive_task: callable, task: int, catalog: str = None):
        self.dump_type = dump_type
        self.action = action
        self.recursive_task = recursive_task
        self.catch_exceptions = getattr(settings, 'DUMP_LOG_EXCEPTIONS', True)

        self.task = GenerateDumpTask.objects.get(id=task)
        self.catalog_id = catalog

    def write(self):
        if self.catalog_id is None:
            nodes = Node.objects.filter(indexable=True).values_list('catalog_id', flat=True)
            for node in nodes:
                self.recursive_task.delay(self.task.id, node)
        if self.catch_exceptions:
            self.run_catching_exceptions()
        else:
            self.action(self.task, self.catalog_id)

        self._finish()

    def _finish(self):
        self.remove_old_dumps()

        _async = settings.RQ_QUEUES['default'].get('ASYNC', True)
        finish = not _async or (_async and not get_queue('default').count)
        if finish:
            self.task.refresh_from_db()
            self.task.status = self.task.FINISHED
            self.task.finished = timezone.now()
            self.task.save()

    def remove_old_dumps(self):
        for dump_name, _ in DumpFile.FILENAME_CHOICES:
            same_file = DumpFile.objects.filter(file_type=self.dump_type,
                                                node__catalog_id=self.catalog_id,
                                                file_name=dump_name)
            old = same_file.order_by('-id')[constants.OLD_DUMP_FILES_AMOUNT:]
            for model in old:
                model.delete()
                for zip_dump_file in model.zipdumpfile_set.all():
                    zip_dump_file.delete()

    def run_catching_exceptions(self):
        try:
            GenerateDumpTask.info(self.task,
                                  f'Comenzando generación de dump {self.dump_type} para catálogo {self.catalog_id}')
            self.action(self.task, self.catalog_id)
        except Exception as e:
            exc = str(e) or format_exc(e)
            msg = f"{self.catalog_id or 'global'}: Error generando el dump {self.dump_type}: {exc}"
            logger.error(msg)
            GenerateDumpTask.info(self.task, msg)
            self._finish()
            raise e
