import os
from abc import abstractmethod

from django.conf import settings
from django.core.files import File
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask, ZipDumpFile


class AbstractDumpGenerator:
    filename = ...

    def __init__(self, task: GenerateDumpTask, fields: dict, catalog: str):
        self.task = task
        self.fields = fields
        self.catalog = catalog

    @abstractmethod
    def generate(self):
        raise NotImplementedError

    def write(self, tmp_file_path, target_filename, zip_file=False):
        with TmpFileWrapper(tmp_file_path) as f:
            dump_file = self.task.dumpfile_set.create(file=File(f),
                                                      file_name=target_filename,
                                                      file_type=DumpFile.TYPE_CSV,
                                                      node=Node.objects.filter(catalog_id=self.catalog).first())
            if zip_file:
                ZipDumpFile.create_from_dump_file(dump_file, tmp_file_path)

    def get_file_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.catalog or '.', self.filename)


class TmpFileWrapper:

    def __init__(self, filepath):
        self.filepath = filepath
        self.fd = None

    def __enter__(self):
        self.fd = open(self.filepath, 'rb')
        return self.fd

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.fd.closed:
            self.fd.close()

        if os.path.exists(self.filepath):
            os.remove(self.filepath)
