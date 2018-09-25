from abc import abstractmethod

from django.core.files import File

from series_tiempo_ar_api.apps.dump.models import CSVDumpTask


class AbstractDumpGenerator:

    def __init__(self, task: CSVDumpTask, fields: dict, catalog: str):
        self.task = task
        self.fields = fields
        self.catalog = catalog

    @abstractmethod
    def generate(self, filepath):
        raise NotImplementedError

    def write(self, tmp_file_path, target_filename):
        if self.catalog is not None:
            target_filename = f'{self.catalog}/{target_filename}'

        with open(tmp_file_path, 'rb') as f:
            self.task.dumpfile_set.create(file_name=target_filename, file=File(f))
