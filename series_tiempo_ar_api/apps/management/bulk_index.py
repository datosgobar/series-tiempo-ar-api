#! coding: utf-8
import unicodecsv

from django_rq import job
from django.utils import timezone

from series_tiempo_ar_api.apps.api.models import Catalog, Dataset
from .models import DatasetIndexingFile
from .strings import DATASET_STATUS, READ_ERROR

CATALOG_HEADER = u'catalog_id'
DATASET_ID_HEADER = u'dataset_identifier'


@job('indexing')
def bulk_index(indexing_file_id):
    indexing_file_model = DatasetIndexingFile.objects.get(id=indexing_file_id)
    toggler = DatasetIndexableToggler()
    try:
        logs_list = toggler.process(indexing_file_model.indexing_file)
        logs = ''
        for log in logs_list:
            logs += log + '\n'

        state = DatasetIndexingFile.PROCESSED
    except ValueError:
        logs = READ_ERROR
        state = DatasetIndexingFile.FAILED

    indexing_file_model.state = state
    indexing_file_model.logs = logs
    indexing_file_model.modified = timezone.now()
    indexing_file_model.save()


class DatasetIndexableToggler(object):

    def __init__(self):
        self.logs = []
        self.catalogs = {}

    def process(self, federation_file):
        self.read_dataset_csv(federation_file)
        self.update_database()
        return self.logs

    def read_dataset_csv(self, federation_file):
        reader = unicodecsv.reader(federation_file)

        headers = reader.next()
        if CATALOG_HEADER not in headers or DATASET_ID_HEADER not in headers:
            raise ValueError

        catalog_idx = headers.index(CATALOG_HEADER)
        dataset_id_idx = headers.index(DATASET_ID_HEADER)

        # Struct con catalog identifiers como keys y listas de datasets como values
        for line in reader:
            catalog = line[catalog_idx]
            dataset_id = line[dataset_id_idx]
            if catalog not in self.catalogs:  # Inicializo
                self.catalogs[catalog] = []

            self.catalogs[catalog].append(dataset_id)

    def update_database(self):
        for catalog, datasets in self.catalogs.items():
            dataset_models = Catalog.objects.get(identifier=catalog).dataset_set
            for dataset in datasets:
                status = 'OK'
                try:
                    dataset_model = dataset_models.get(identifier=dataset)
                    dataset_model.indexable = True
                    dataset_model.save()
                except Dataset.DoesNotExist:
                    status = 'ERROR'

                self.logs.append(DATASET_STATUS.format(catalog, dataset, status))
