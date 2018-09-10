from abc import abstractmethod

from series_tiempo_ar_api.apps.dump.models import CSVDumpTask


class AbstractDumpGenerator:

    def __init__(self, task: CSVDumpTask, fields: dict):
        self.task = task
        self.fields = fields

    @abstractmethod
    def generate(self, filepath):
        raise NotImplementedError
