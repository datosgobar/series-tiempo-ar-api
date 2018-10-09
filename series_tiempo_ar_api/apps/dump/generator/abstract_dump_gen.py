import os
from abc import abstractmethod

from django.conf import settings
from django.core.files import File
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask


class AbstractDumpGenerator:
    filename = ...

    def __init__(self, task: GenerateDumpTask, fields: dict, catalog: str):
        self.task = task
        self.fields = fields
        self.catalog = catalog

    @abstractmethod
    def generate(self):
        raise NotImplementedError

    def write(self, tmp_file_path, target_filename):
        with open(tmp_file_path, 'rb') as f:
            self.task.dumpfile_set.create(file=File(f),
                                          file_name=target_filename,
                                          file_type=DumpFile.TYPE_CSV,
                                          node=Node.objects.filter(catalog_id=self.catalog).first())

    def get_file_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.catalog or '.', self.filename)
