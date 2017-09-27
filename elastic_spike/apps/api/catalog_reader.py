#! coding: utf-8
import json
from tempfile import NamedTemporaryFile

import requests
from django.core.files import File
from pydatajson import DataJson
from pydatajson_ts.validations import validate_distribution
from pydatajson_ts.search import get_time_series_distributions
from pydatajson.search import get_dataset
from .models import Catalog, Dataset, Distribution, Field
import pandas as pd


class ReaderPipeline(object):

    def __init__(self, catalog):
        self.catalog = DataJson(catalog)
        self.run()

    def run(self):
        scrapper = Scrapper()
        scrapper.run(self.catalog)
        DatabaseLoader().run(self.catalog, scrapper.distributions)


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self):
        self.dataset_cache = {}
        self.catalog_model = None

    def run(self, catalog, distributions):
        """Guarda las distribuciones de la lista 'distributions',
        asociadas al catálogo 'catalog, en la base de datos, junto con
        todos los metadatos de distinto nivel (catalog, dataset)
        
        Args:
            catalog (DataJson)
            distributions (list)
        """
        self.catalog_model = self._catalog_model(catalog)
        for distribution in distributions:
            distribution_model = self._distribution_model(catalog,
                                                          distribution)

            fields = distribution['field']
            self._save_fields(distribution_model, fields)

    def _dataset_model(self, dataset):
        """Crea o actualiza el modelo del dataset a partir de un
        diccionario que lo representa
        """
        if dataset['identifier'] in self.dataset_cache:
            return self.dataset_cache[dataset['identifier']]

        dataset = dataset.copy()
        # Borro las distribuciones, de existir. Solo guardo metadatos
        dataset.pop('distribution', None)
        title = dataset.pop('title', None)
        dataset_model, _ = Dataset.objects.get_or_create(
            title=title,
            catalog=self.catalog_model
        )
        dataset_model.metadata = json.dumps(dataset)
        dataset_model.save()

        self.dataset_cache[dataset['identifier']] = dataset_model
        return dataset_model

    @staticmethod
    def _catalog_model(catalog):
        """Crea o actualiza el catalog model con el título pedido a partir
        de el diccionario de metadatos de un catálogo
        """
        catalog = catalog.copy()
        # Borro el dataset, de existir. Solo guardo metadatos
        catalog.pop('dataset', None)
        title = catalog.pop('title', None)
        catalog_model, _ = Catalog.objects.get_or_create(title=title)
        catalog_model.metadata = json.dumps(catalog)
        catalog_model.save()
        return catalog_model

    def _distribution_model(self, catalog, distribution):
        """Crea o actualiza el modelo de la distribución a partir de
        un diccionario que lo representa
        """
        distribution = distribution.copy()
        # Borro los fields, de existir. Sólo guardo metadatos
        distribution.pop('field', None)
        title = distribution.pop('title', None)
        url = distribution.pop('downloadURL', None)

        dataset = get_dataset(catalog,
                              identifier=distribution.get('dataset_identifier'))

        dataset.pop('distribution', None)
        dataset_model = self._dataset_model(dataset)
        distribution_model, _ = Distribution.objects.get_or_create(
            title=title,
            dataset=dataset_model
        )
        distribution_model.metadata = json.dumps(distribution)
        distribution_model.download_url = url
        self._read_file(url, distribution_model)
        distribution_model.save()
        return distribution_model

    @staticmethod
    def _read_file(file_url, distribution_model):
        """Descarga y lee el archivo de la distribución. Por razones
        de performance, NO hace un save() a la base de datos.
        
        Args:
            file_url (str)
            distribution_model (Distribution)
        """
        request = requests.get(file_url, stream=True)

        if request.status_code != 200:
            return False

        lf = NamedTemporaryFile()

        for block in request.iter_content(1024*8):
            if not block:
                break

            lf.write(block)

        distribution_model.data_file = File(lf)
        distribution_model.save()

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
