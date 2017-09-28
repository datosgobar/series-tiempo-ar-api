#! coding: utf-8
import json
from tempfile import NamedTemporaryFile

import requests
import pandas as pd
from django.core.files import File
from django.conf import settings
from pydatajson import DataJson
from pydatajson_ts.validations import validate_distribution
from pydatajson_ts.search import get_time_series_distributions
from pydatajson.search import get_dataset
from elasticsearch import Elasticsearch

from .models import Catalog, Dataset, Distribution, Field


class ReaderPipeline(object):

    def __init__(self, catalog, index_only):
        self.catalog = DataJson(catalog)
        self.index_only = index_only
        self.run()

    def run(self):
        distributions = None
        if not self.index_only:
            scrapper = Scrapper()
            scrapper.run(self.catalog)
            distributions = scrapper.distributions
            DatabaseLoader().run(self.catalog, distributions)
        Indexer().run(distributions)


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self):
        self.distribution_models = []
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
        self.distribution_models.append(distribution_model)
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
            title = field.pop('title')
            field_model, _ = Field.objects.get_or_create(
                series_id=series_id,
                distribution=distribution_model
            )
            field_model.title = title
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


class Indexer(object):
    """Lee distribuciones y las indexa a través de un bulk create en
    Elasticsearch
    """

    def __init__(self):
        self.elastic = Elasticsearch()
        self.bulk_body = ''

    def run(self, distributions=None):
        """Indexa en Elasticsearch todos los datos de las
        distribuciones guardadas en la base de datos, o las
        especificadas por el iterable 'distributions'
        """

        if not distributions:
            distributions = Distribution.objects.exclude(data_file='')

        for distribution in distributions:
            fields = distribution.field_set.all()
            df = pd.read_csv(distribution.data_file,
                             parse_dates=['indice_tiempo'])
            df = df.set_index('indice_tiempo')
            valid = True
            for field in fields:
                if field.title not in df:
                    # Error fatal, no es válido el csv
                    valid = False
                    break

            if valid:
                self._index(df, fields)

    def _index(self, df, fields):
        year_ago_shift = 4  # todo: calcular según periodicidad

        for field in fields:
            # Mapping del indicador
            if not self.elastic.indices.exists_type(index=settings.TS_INDEX,
                                                    doc_type=field.series_id):
                self.elastic.indices.put_mapping(index=settings.TS_INDEX,
                                                 doc_type=field.series_id,
                                                 body=settings.MAPPING)

            self.generate_properties(df[field.title],
                                     field.series_id,
                                     year_ago_shift)
            self.elastic.bulk(index=settings.TS_INDEX,
                              doc_type=field.series_id,
                              body=self.bulk_body)

    def generate_properties(self, serie, serie_id, shift):
        """Genera el cuerpo del bulk create request a elasticsearch.
        Este cuerpo son varios JSON delimitados por newlines, con los
        valores de los campos a indexar de cada serie. Ver:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
        """
        result = ''
        properties_template = {
            'timestamp': None,
            'value': 0,
            'change': 0,
            'percent_change': 0,
            'change_a_year_ago': 0,
            'percent_change_a_year_ago': 0
        }
        change = serie.diff(1)
        change_a_year_ago = serie.diff(shift)
        percent_change = serie.pct_change(1)
        pct_change_a_year_ago = serie.pct_change(shift)
        for index, value in serie.iteritems():
            properties = properties_template.copy()

            timestamp = str(index.to_pydatetime().date())
            properties['timestamp'] = timestamp
            properties['value'] = value
            properties['change'] = change[timestamp]
            properties['percent_change'] = percent_change[timestamp]
            properties['change_a_year_ago'] = change_a_year_ago[timestamp]
            properties['percent_change_a_year_ago'] = \
                pct_change_a_year_ago[timestamp]

            index_data = {
                "index": {"_id": timestamp, "_type": serie_id}
            }

            result += json.dumps(index_data) + '\n'
            result += json.dumps(properties) + '\n'

        self.bulk_body += result
