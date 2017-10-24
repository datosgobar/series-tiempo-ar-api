#! coding: utf-8
import json
import logging
from tempfile import NamedTemporaryFile

import numpy as np
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files import File
from elasticsearch import ConnectionTimeout
from elasticsearch_dsl import Search
from pydatajson import DataJson
from pydatajson.search import get_dataset
from series_tiempo_ar.search import get_time_series_distributions
from series_tiempo_ar.validations import validate_distribution
from series_tiempo_ar.helpers import freq_iso_to_pandas

from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, \
    Distribution, Field
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance

logger = logging.Logger(__name__)
logger.addHandler(logging.StreamHandler())


class ReaderPipeline(object):

    def __init__(self, catalog, index_only=False):
        """Ejecuta el pipeline de lectura, guardado e indexado de datos
        y metadatos sobre el catálogo especificado

        Args:
            catalog (DataJson): DataJson del catálogo a parsear
            index_only (bool): Correr sólo la indexación o no
        """

        self.catalog = catalog
        self.index_only = index_only
        self.run()

    def run(self):
        distribution_models = None
        if not self.index_only:
            scraper = Scraper()
            scraper.run(self.catalog)
            distributions = scraper.distributions
            loader = DatabaseLoader()
            loader.run(self.catalog, distributions)
            distribution_models = loader.distribution_models
        Indexer().run(distribution_models)


class Scraper(object):

    def __init__(self, read_local=False):
        self.distributions = []
        self.fields = []
        self.read_local = read_local

    def run(self, catalog):
        """Valida las distribuciones de series de tiempo de un catálogo
        entero a partir de su URL, o archivo fuente
        """
        catalog = DataJson(catalog)
        distributions = get_time_series_distributions(catalog)
        for distribution in distributions[:]:
            distribution_id = distribution['identifier']
            if not self.read_local:
                if not self._validate_url(distribution):
                    distributions.remove(distribution)
                    continue

            url = distribution['downloadURL']
            dataset = catalog.get_dataset(distribution['dataset_identifier'])
            df = pd.read_csv(url, parse_dates=[settings.INDEX_COLUMN])
            df = df.set_index(settings.INDEX_COLUMN)

            try:
                validate_distribution(df,
                                      catalog,
                                      dataset,
                                      distribution)
            except ValueError as e:
                msg = u'Desestimada la distribución {}. Razón: {}'.format(
                    distribution_id,
                    e.message
                )
                logger.info(msg)
                distributions.remove(distribution)

        self.distributions = distributions

    @staticmethod
    def _validate_url(distribution):
        distribution_id = distribution['identifier']
        url = distribution.get('downloadURL')
        if not url or requests.head(url).status_code != 200:
            msg = u'URL inválida en distribución {}'.format(distribution_id)
            logger.info(msg)
            return False
        return True


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self, read_local=False):
        self.distribution_models = []
        self.dataset_cache = {}
        self.catalog_model = None
        self.read_local = read_local

    def run(self, catalog, distributions):
        """Guarda las distribuciones de la lista 'distributions',
        asociadas al catálogo 'catalog, en la base de datos, junto con
        todos los metadatos de distinto nivel (catalog, dataset)

        Args:
            catalog (DataJson)
            distributions (list)
        """
        catalog = DataJson(catalog)
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
        identifier = dataset['identifier']
        dataset_model, _ = Dataset.objects.get_or_create(
            identifier=identifier,
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
        title = catalog.get('title')
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
        identifier = distribution['identifier']
        url = distribution.get('downloadURL')

        dataset = get_dataset(catalog,
                              identifier=distribution.get('dataset_identifier'))

        dataset.pop('distribution', None)
        dataset_model = self._dataset_model(dataset)
        distribution_model, _ = Distribution.objects.get_or_create(
            identifier=identifier,
            dataset=dataset_model
        )
        distribution_model.metadata = json.dumps(distribution)
        distribution_model.download_url = url
        distribution_model.periodicity = periodicity
        self._read_file(url, distribution_model)
        distribution_model.save()
        self.distribution_models.append(distribution_model)
        return distribution_model

    def _read_file(self, file_url, distribution_model):
        """Descarga y lee el archivo de la distribución. Por razones
        de performance, NO hace un save() a la base de datos.

        Args:
            file_url (str)
            distribution_model (Distribution)
        """
        if self.read_local:  # Usado en debug y testing
            distribution_model.data_file = File(open(file_url))
            return

        request = requests.get(file_url, stream=True)

        if request.status_code != 200:
            return False

        lf = NamedTemporaryFile()

        block_size = 1024 * 8
        for block in request.iter_content(block_size):
            lf.write(block)

        if distribution_model.data_file:
            distribution_model.data_file.delete()

        distribution_model.data_file = File(lf)

    @staticmethod
    def _save_fields(distribution_model, fields):
        for field in fields:
            if field.get('specialType') == 'time_index':
                continue

            series_id = field.get('id')
            title = field.get('title')
            field_model, _ = Field.objects.get_or_create(
                series_id=series_id,
                title=title,
                distribution=distribution_model
            )
            field_model.metadata = json.dumps(field)
            field_model.save()


class Indexer(object):
    """Lee distribuciones y las indexa a través de un bulk create en
    Elasticsearch
    """
    block_size = 1e6

    default_value = 0

    def __init__(self, index=settings.TS_INDEX):
        self.elastic = ElasticInstance()
        self.index = index
        self.indexed_fields = set()

    def run(self, distributions=None):
        """Indexa en Elasticsearch todos los datos de las
        distribuciones guardadas en la base de datos, o las
        especificadas por el iterable 'distributions'
        """
        self.init_index()

        # Optimización: Desactivo el refresh de los datos mientras indexo
        self.elastic.indices.put_settings(
            index=self.index,
            body={'index': {
                'refresh_interval': -1
            }}
        )

        if not distributions:
            distributions = Distribution.objects.exclude(data_file='')

        fields_count = 0
        for distribution in distributions:
            fields_count += distribution.field_set.count()
        msg = u'Inicio de la indexación. Cantidad de fields a indexar: %d'
        logger.info(msg, fields_count)

        bulk_body = ''
        for distribution in distributions:
            fields = distribution.field_set.all()
            fields = {field.title: field.series_id for field in fields}
            df = self.init_df(distribution, fields)

            bulk_body += self.generate_properties(df, fields)

            if len(bulk_body) > self.block_size:
                retry = 3
                while retry:
                    try:
                        retry -= 1
                        self._put_data(bulk_body)
                        break
                    except ConnectionTimeout:
                        continue
                bulk_body = ''

        if bulk_body:
            self._put_data(bulk_body)

        # Reactivo el proceso de replicado una vez finalizado
        self.elastic.indices.put_settings(
            index=self.index,
            body={
                'index': {
                    'refresh_interval': settings.TS_REFRESH_INTERVAL
                }
            }
        )
        segments = settings.FORCE_MERGE_SEGMENTS
        self.elastic.indices.forcemerge(index=self.index,
                                        max_num_segments=segments)

        msg = u'Fin de la indexación. %d series indexadas.'
        logger.info(msg, len(self.indexed_fields))

    @staticmethod
    def init_df(distribution, fields):
        """Inicializa el DataFrame del CSV de la distribución pasada,
        seteando el índice de tiempo correcto y validando las columnas
        dentro de los datos

        Args:
            distribution (Distribution): modelo de distribución válido
            fields (dict): diccionario con estructura titulo: serie_id
        """

        df = pd.read_csv(distribution.data_file.file,
                         parse_dates=[settings.INDEX_COLUMN])
        df = df.set_index(settings.INDEX_COLUMN)

        # Borro las columnas que no figuren en los metadatos
        for column in df.columns:
            if column not in fields:
                df.drop(column, axis=1, inplace=True)
        columns = df.columns

        data = np.array(df)
        freq = freq_iso_to_pandas(distribution.periodicity)
        new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

        if freq == 'D' and new_index.size > df.index.size:
            new_index = pd.date_range(df.index[0], df.index[-1], freq='B')\

        return pd.DataFrame(index=new_index, data=data, columns=columns)

    def init_index(self):
        if not self.elastic.indices.exists(self.index):
            self.elastic.indices.create(self.index,
                                        body=settings.INDEX_CREATION_BODY)

    def generate_properties(self, df, fields):
        """Genera el cuerpo del bulk create request a elasticsearch.
        Este cuerpo son varios JSON delimitados por newlines, con los
        valores de los campos a indexar de cada serie. Ver:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
        """

        # Es mucho más eficiente iterar el dataframe fila por fila. Calculo
        # todas las diferencias absolutas y porcentuales previamente
        data = {
            'change': df.diff(1),
            'change_a_year_ago': self._year_ago_operation(df, self._change),
            'percent_change': df.pct_change(1),
            'percent_change_a_year_ago':
                self._year_ago_operation(df, self._pct_change)
        }
        result = ''
        for index, values in df.iterrows():

            timestamp = str(index.date())
            for column, value in values.iteritems():
                properties = {
                    'timestamp': timestamp,
                    'series_id': fields[column]
                }

                if np.isfinite(value):
                    properties['value'] = value

                for prop_name, df in data.iteritems():
                    value = self._get_value(df, column, index)
                    if np.isfinite(value):
                        properties[prop_name] = value

                index_data = {
                    "index": {
                        "_id": fields[column] + '-' + timestamp,
                        "_type": settings.TS_DOC_TYPE
                    }
                }

                result += json.dumps(index_data) + '\n'
                result += json.dumps(properties) + '\n'
                self.indexed_fields.add(fields[column])

        for series_id in fields.values():
            if series_id not in self.indexed_fields:
                msg = 'Serie %s no encontrada en su dataframe'
                logger.info(msg, series_id)
                self._handle_missing_series(series_id)

        return result

    def _handle_missing_series(self, series_id):
        # Si no hay datos previos indexados, borro la entrada de la DB
        search = Search(using=self.elastic).filter('match', series_id=series_id)
        results = search.execute()
        if not results:
            Field.objects.get(series_id=series_id).delete()

    def _get_value(self, df, col, index):
        """Devuelve el valor del df[col][index] o nan si no es válido.
        Evita Cargar Infinity y NaN en Elasticsearch
        """
        return df[col][index] if np.isfinite(df[col][index]) else \
            self.default_value

    def _put_data(self, data):
        """Envía los datos a la instancia de Elasticsearch y valida
        resultados
        """

        response = self.elastic.bulk(index=self.index,
                                     body=data,
                                     request_timeout=settings.REQUEST_TIMEOUT)

        for item in response['items']:
            if item['index']['status'] not in settings.VALID_STATUS_CODES:
                msg = "Debug: No se creó bien el item {} de {}. " \
                      "Status code {}".format(
                          item['index']['_id'],
                          item['index']['_type'],
                          item['index']['status'])
                logger.warn(msg)

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
                if value != self.default_value:
                    if freq != 'B':
                        validate = False

                    value = operation(val, value)

                array[x][y] = value
                x += 1
            y += 1

        return pd.DataFrame(index=df.index, data=array, columns=df.columns)

    def _get_value_a_year_ago(self, df, idx, col, validate=False):
        """Devuelve el valor de la serie determinada por df[col] un
        año antes del índice de tiempo 'idx'. Hace validación de si
        existe el índice o no según 'validate' (operación costosa)
        """

        value = self.default_value
        year_ago_idx = idx.date() - relativedelta(years=1)
        if not validate:
            value = df[col][year_ago_idx]
        else:
            if year_ago_idx in df[col]:
                value = df[col][year_ago_idx]

        return value

    def _pct_change(self, x, y):
        if x == 0:
            return self.default_value
        return float(x - y) / y

    @staticmethod
    def _change(x, y):
        return x - y
