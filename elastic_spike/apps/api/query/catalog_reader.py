#! coding: utf-8
import json
from tempfile import NamedTemporaryFile

import numpy as np
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files import File
from elasticsearch import ConnectionTimeout
from pydatajson import DataJson
from pydatajson.search import get_dataset
from pydatajson_ts.search import get_time_series_distributions
from pydatajson_ts.validations import validate_distribution
from pydatajson_ts.helpers import freq_iso_to_pandas

from elastic_spike.apps.api.models import Catalog, Dataset, Distribution, Field
from elastic_spike.apps.api.query.elastic import ElasticInstance
import logging


class ReaderPipeline(object):

    def __init__(self, catalog, index_only):
        self.catalog = DataJson(catalog)
        self.index_only = index_only
        self.run()

    def run(self):
        distribution_models = None
        if not self.index_only:
            scrapper = Scraper()
            scrapper.run(self.catalog)
            distributions = scrapper.distributions
            loader = DatabaseLoader()
            loader.run(self.catalog, distributions)
            distribution_models = loader.distribution_models
        Indexer().run(distribution_models)


class Scraper(object):

    logger = logging.getLogger(__name__)

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
                msg = u'URL inválida en distribución {}'.format(distribution_id)
                self.logger.info(msg)
                distributions.remove(distribution)
                continue
            dataset = catalog.get_dataset(distribution['dataset_identifier'])
            df = pd.read_csv(url, parse_dates=[settings.INDEX_COLUMN])
            df = df.set_index(settings.INDEX_COLUMN)

            try:
                validate_distribution(df,
                                      catalog,
                                      dataset,
                                      distribution,
                                      distribution_id)
            except ValueError as e:
                msg = u'Desestimada la distribución {}. Razón: {}'.format(
                    distribution_id,
                    e.message
                )
                self.logger.info(msg)
                distributions.remove(distribution)

        self.distributions = distributions


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
            fields = distribution['field']
            time_distribution = False
            periodicity = None
            for field in fields:
                if field.get('specialType') == 'time_index':
                    periodicity = field.get('specialTypeDetail')
                    time_distribution = True
                    break

            if time_distribution:
                distribution_model = self._distribution_model(catalog,
                                                              distribution,
                                                              periodicity)

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

    def _distribution_model(self, catalog, distribution, periodicity):
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
        distribution_model.periodicity = periodicity
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


class Indexer(object):
    """Lee distribuciones y las indexa a través de un bulk create en
    Elasticsearch
    """
    block_size = 1e6

    logger = logging.Logger(__name__)

    def __init__(self):
        self.elastic = ElasticInstance()
        self.bulk_body = ''

    def run(self, distributions=None):
        """Indexa en Elasticsearch todos los datos de las
        distribuciones guardadas en la base de datos, o las
        especificadas por el iterable 'distributions'
        """
        self.init_index()

        # Optimización: Desactivo el refresh de los datos mientras indexo
        self.elastic.indices.put_settings(
            index=settings.TS_INDEX,
            body={'index': {
                'refresh_interval': -1
            }}
        )

        if not distributions:
            distributions = Distribution.objects.exclude(data_file='')

        for distribution in distributions:
            fields = distribution.field_set.all()
            df = self.init_df(distribution)

            fields = {field.title: field.series_id for field in fields}
            self.generate_properties(df, fields)

            if len(self.bulk_body) > self.block_size:
                retry = 3
                while retry:
                    try:
                        retry -= 1
                        self._put_data()
                        break
                    except ConnectionTimeout:
                        continue

                self.bulk_body = ''

        # Reactivo el proceso de replicado una vez finalizado
        self.elastic.indices.put_settings(
            index=settings.TS_INDEX,
            body={
                'index': {
                    'refresh_interval': settings.TS_REFRESH_INTERVAL
                }
            }
        )

    @staticmethod
    def init_df(distribution):
        df = pd.read_csv(distribution.data_file,
                         parse_dates=[settings.INDEX_COLUMN])
        df = df.set_index(settings.INDEX_COLUMN)
        freq = freq_iso_to_pandas(distribution.periodicity)
        new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

        if freq == 'D' and new_index.size > df.index.size:
            new_index = pd.date_range(df.index[0], df.index[-1], freq='B')

        columns = df.columns
        data = np.array(df)
        df = pd.DataFrame(index=new_index, data=data, columns=columns)
        return df

    def init_index(self):
        if not self.elastic.indices.exists(settings.TS_INDEX):
            self.elastic.indices.create(settings.TS_INDEX,
                                        body=settings.INDEX_CREATION_BODY)

    def generate_properties(self, df, fields):
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
            'percent_change_a_year_ago': 0,
            'series_id': ''
        }

        # Es mucho más eficiente iterar el dataframe fila por fila. Calculo
        # todas las diferencias absolutas y porcentuales previamente
        change = df.diff(1)
        change_a_year_ago = self._year_ago_operation(df, self._change)
        percent_change = df.pct_change(1)
        pct_change_a_year_ago = self._year_ago_operation(df, self._pct_change)

        for index, values in df.iterrows():
            properties = properties_template.copy()

            timestamp = str(index.date())
            for column, value in values.iteritems():
                if not np.isfinite(value):
                    continue

                if column not in fields:
                    continue

                properties['timestamp'] = timestamp
                properties['series_id'] = fields[column]
                properties['value'] = value
                properties['change'] = self._get_value(change, column, index)

                properties['percent_change'] = \
                    self._get_value(percent_change, column, index)

                properties['change_a_year_ago'] = \
                    self._get_value(change_a_year_ago, column, index)

                properties['percent_change_a_year_ago'] = \
                    self._get_value(pct_change_a_year_ago, column, index)

                index_data = {
                    "index": {
                        "_id": column + '-' + timestamp,
                        "_type": settings.TS_DOC_TYPE
                    }
                }

                result += json.dumps(index_data) + '\n'
                result += json.dumps(properties) + '\n'

        self.bulk_body += result

    @staticmethod
    def _get_value(df, col, index):
        """Devuelve el valor del df[col][index] o nan si no es válido.
        Evita Cargar Infinity en Elasticsearch
        """
        return df[col][index] if not np.isinf(df[col][index]) else np.nan

    def _put_data(self):
        """Envía los datos a la instancia de Elasticsearch y valida
        resultados
        """

        response = self.elastic.bulk(index=settings.TS_INDEX,
                                     body=self.bulk_body,
                                     timeout="30s")

        for item in response['items']:
            if item['index']['status'] not in (200, 201):
                msg = "Debug: No se creó bien el item {} de {}. " \
                      "Status code {}".format(
                        item['index']['_id'],
                        item['index']['_type'],
                        item['index']['status'])
                self.logger.warn(msg)

    def _year_ago_operation(self, df, operation):
        """Ejecuta operation entre cada valor de df y el valor del
        mismo dato el año pasado.
        Args:
            df (pd.DataFrame)
            operation (callable): Función con parámetros x e y a aplicar
            
        Returns:
            pd.DataFrame
        """
        # Array de datos del nuevo DataFrame, inicialmente vacío
        array = np.ndarray(df.shape)
        freq = df.index.freq.freqstr
        y = 0
        for col, vals in df.iteritems():
            x = 0
            validate = True
            for idx, val in vals.iteritems():
                value = self._get_value_a_year_ago(df, idx, col, validate)
                if not np.isnan(value):
                    if freq != 'B':
                        validate = False

                    value = operation(val, value)

                array[x][y] = value
                x += 1
            y += 1

        return pd.DataFrame(index=df.index, data=array, columns=df.columns)

    @staticmethod
    def _get_value_a_year_ago(df, idx, col, validate=False):
        value = np.nan
        year_ago_idx = idx.date() - relativedelta(years=1)
        if not validate:
            value = df[col][year_ago_idx]
        else:
            if year_ago_idx in df[col]:
                value = df[col][year_ago_idx]

        return value

    @staticmethod
    def _pct_change(x, y):
        if x == 0:
            return np.nan
        return float(x - y / x)

    @staticmethod
    def _change(x, y):
        return x - y
