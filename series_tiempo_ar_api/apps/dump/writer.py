import logging

from traceback import format_exc

from django.utils import timezone
from django.conf import settings
from django_rq import get_queue
from django_datajsonar.models import Node

from .models import GenerateDumpTask
logger = logging.Logger(__name__)


class Writer:

    def __init__(self, tag: str, action: callable, recursive_task: callable, task: int, catalog: str = None):
        self.tag = tag
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
        _async = settings.RQ_QUEUES['default'].get('ASYNC', True)
        finish = not _async or (_async and not get_queue('default').count)
        if finish:
            self.task.refresh_from_db()
            self.task.status = self.task.FINISHED
            self.task.finished = timezone.now()
            self.task.save()

    def run_catching_exceptions(self):
        try:
            self.action(self.task, self.catalog_id)
        except Exception as e:
            exc = str(e) or format_exc(e)
            msg = f"{self.catalog_id or 'global'}: Error generando el dump {self.tag}: {exc}"
            logger.error(msg)
            GenerateDumpTask.info(self.task, msg)
            self._finish()
            raise e
