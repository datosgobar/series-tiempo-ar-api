#! coding: utf-8
import json

from pydatajson import DataJson
from pydatajson_ts.validations import validate_distribution
from pydatajson_ts.search import get_time_series_distributions
from pydatajson.search import get_distribution, get_dataset, \
    get_catalog_metadata
from pydatajson.readers import read_catalog
from .models import Catalog, Dataset, Distribution, Field
import pandas as pd


class ReaderPipeline(object):

    def __init__(self, catalog):
        self.catalog = read_catalog(catalog)
        self.run()

    def run(self):
        scrapper = Scrapper()
        scrapper.run(self.catalog)
        DatabaseLoader().run(self.catalog, scrapper.fields)


class DatabaseLoader(object):

    def run(self, catalog, fields):
        for field in fields:
            if field.get('specialType') == 'time_index':
                continue

            series_id = field.pop('id')
            distribution_identifier = field.get('distribution_identifier')
            if not distribution_identifier:
                continue
            distribution = get_distribution(
                catalog,
                identifier=distribution_identifier
            )
            distribution.pop('field')
            distribution_model = self._distribution_model(catalog, distribution)

            field_model, _ = Field.objects.get_or_create(
                series_id=series_id,
                distribution=distribution_model
            )
            field_model.metadata = json.dumps(field)
            field_model.save()

    def _dataset_model(self, catalog, dataset):
        title = dataset.pop('title', None)
        catalog_meta = get_catalog_metadata(catalog)
        catalog_model = self._catalog_model(catalog_meta)
        dataset_model, _ = Dataset.objects.get_or_create(
            title=title,
            catalog=catalog_model
        )
        dataset_model.metadata = json.dumps(dataset)
        dataset_model.save()
        return dataset_model

    @staticmethod
    def _catalog_model(catalog):
        """Crea o actualiza el catalog model con el título pedido a partir
        de el diccionario de metadatos de un catálogo
        """
        title = catalog.pop('title', None)
        catalog_model, _ = Catalog.objects.get_or_create(title=title)
        catalog_model.metadata = json.dumps(catalog)
        catalog_model.save()
        return catalog_model

    def _distribution_model(self, catalog, distribution):
        title = distribution.pop('title', None)
        url = distribution.pop('downloadURL', None)

        dataset = get_dataset(catalog,
                              identifier=distribution.get('dataset_identifier'))

        dataset.pop('distribution')
        dataset_model = self._dataset_model(catalog, dataset)
        distribution_model, _ = Distribution.objects.get_or_create(
            title=title,
            dataset=dataset_model
        )
        distribution_model.metadata = json.dumps(distribution)
        distribution_model.download_url = url
        distribution_model.save()
        return distribution_model

    @staticmethod
    def _save_fields(distribution_model, fields):
        for field in fields:
            if field.get('specialType') == 'time_index':
                continue

            series_id = field.pop('id')
            field_model, _ = Field.objects.get_or_create(
                series_id=series_id,
                distribution=distribution_model
            )
            field_model.metadata = json.dumps(field)
            field_model.save()


class Scrapper(object):

    def __init__(self):
        self.distributions = []
        self.fields = []

    def run(self, catalog):
        """Valida las distribuciones de series de tiempo de un catálogo 
        entero a partir de su URL, o archivo fuente
        """
        catalog = DataJson(catalog)
        distributions = get_time_series_distributions(catalog)
        for distribution in distributions[:]:
            distribution_id = distribution['identifier']
            url = distribution.get('downloadURL')
            if not url:
                continue
            dataset = catalog.get_dataset(distribution['dataset_identifier'])
            df = pd.read_csv(url, parse_dates=['indice_tiempo'])
            df = df.set_index('indice_tiempo')
            try:
                validate_distribution(df,
                                      catalog,
                                      dataset,
                                      distribution,
                                      distribution_id)
            except ValueError:
                distributions.remove(distribution)

        self.distributions = distributions
