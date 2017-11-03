#! coding: utf-8
from __future__ import division

import json
import logging
from tempfile import NamedTemporaryFile

import numpy as np
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files import File
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Search
from pydatajson import DataJson
from pydatajson.search import get_dataset
from series_tiempo_ar.search import get_time_series_distributions
from series_tiempo_ar.validations import validate_distribution
from series_tiempo_ar.helpers import freq_iso_to_pandas

from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, \
    Distribution, Field
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.helpers import \
    freq_pandas_to_index_offset
from .indexing.scraping import get_scraper

logger = logging.Logger(__name__)
logger.addHandler(logging.StreamHandler())

# Ignora divisiones por cero, no nos molesta el NaN
np.seterr(divide='ignore', invalid='ignore')


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
            scraper = get_scraper()
            scraper.run(self.catalog)
            distributions = scraper.distributions
            loader = DatabaseLoader()
            loader.run(self.catalog, distributions)
            distribution_models = loader.distribution_models
        Indexer().run(distribution_models)

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
        logger.info("Comienzo de la escritura a base de datos")
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
        logger.info("Fin de la escritura a base de datos")

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
        self.bulk_actions = []

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

        for distribution in distributions:
            fields = distribution.field_set.all()
            fields = {field.title: field.series_id for field in fields}
            df = self.init_df(distribution, fields)

            self.generate_properties(df, fields)

        logger.info("Inicio del bulk request a ES")

        for success, info in parallel_bulk(self.elastic, self.bulk_actions):
            if not success:
                logger.warn(u"Error en la indexación: %s", info)

        logger.info("Fin del bulk request a ES")

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

        # Chequeo de series de días hábiles (business days)
        if freq == 'D' and new_index.size > df.index.size:
            new_index = pd.date_range(df.index[0], df.index[-1], freq='B')\

        return pd.DataFrame(index=new_index, data=data, columns=columns)

    def init_index(self):
        if not self.elastic.indices.exists(self.index):
            self.elastic.indices.create(self.index,
                                        body=settings.INDEX_CREATION_BODY)

    def generate_properties(self, df, fields):
        df.apply(self.process_column, args=[fields])

        # Manejo de series faltantes
        for series_id in fields.values():
            if series_id not in self.indexed_fields:
                msg = 'Serie %s no encontrada en su dataframe'
                logger.info(msg, series_id)
                self._handle_missing_series(series_id)

    def process_column(self, col, fields):
        """Procesa una columna del DataFrame: calcula los valores de
        diferencias, porcentuales y anuales, los guarda en un DataFrame
        y luego indexa los valores fila por fila"""

        # Filtro de valores nulos iniciales/finales
        col = col[col.first_valid_index():col.last_valid_index()]

        freq = col.index.freq.freqstr
        df = pd.DataFrame()
        df['value'] = col
        df['change'] = col.diff(1)
        df['percent_change'] = col.pct_change(1)
        df['change_a_year_ago'] = \
            self._year_ago_column(col, self._change, freq)
        df['percent_change_a_year_ago'] = \
            self._year_ago_column(col, self._pct_change, freq)

        df.apply(self.elastic_index, axis=1, args=[fields[col.name]])

    def elastic_index(self, row, series_id):
        """Indexa la fila de datos correspondientes a una serie en ES

        la fila tiene forma de iterable con los datos de un único
        valor de la serie: el valor real, su variación inmnediata,
        porcentual, etc
        """

        # Borrado de la parte de tiempo del timestamp
        timestamp = str(row.name)
        timestamp = timestamp[:timestamp.find('T')]

        action = {
            "_index": self.index,
            "_type": settings.TS_DOC_TYPE,
            "_id": None,
            "_source": {}
        }

        source = {
            'timestamp': timestamp,
            'series_id': series_id
        }

        for column, value in row.iteritems():
            if value and np.isfinite(value):
                source[column] = value

        action['_id'] = series_id + '-' + timestamp
        action['_source'] = source
        self.bulk_actions.append(action)
        self.indexed_fields.add(series_id)

    def _handle_missing_series(self, series_id):
        # Si no hay datos previos indexados, borro la entrada de la DB
        search = Search(using=self.elastic,
                        index=self.index).filter('match', series_id=series_id)
        results = search.execute()
        if not results:
            Field.objects.get(series_id=series_id).delete()

    def _get_value(self, df, col, index):
        """Devuelve el valor del df[col][index] o nan si no es válido.
        Evita Cargar Infinity y NaN en Elasticsearch
        """
        if index not in df[col]:
            return self.default_value

        return df[col][index] if np.isfinite(df[col][index]) else \
            self.default_value

    def _year_ago_column(self, col, operation, freq):
        """Aplica operación entre los datos de una columna y su valor
        un año antes. Devuelve una nueva serie de pandas
        """
        array = []
        offset = freq_pandas_to_index_offset(freq) or 0
        if offset:
            values = col.values
            array = operation(values[offset:], values[:-offset])
        else:
            for idx, val in col.iteritems():
                value = self._get_value_a_year_ago(idx, col, validate=True)
                if value != self.default_value:
                    array.append(operation(val, value))
                else:
                    array.append(None)

        return pd.Series(array, index=col.index[offset:])

    def _get_value_a_year_ago(self, idx, col, validate=False):
        """Devuelve el valor de la serie determinada por df[col] un
        año antes del índice de tiempo 'idx'. Hace validación de si
        existe el índice o no según 'validate' (operación costosa)
        """

        value = self.default_value
        year_ago_idx = idx.date() - relativedelta(years=1)
        if not validate:
            if year_ago_idx not in col.index:
                return self.default_value

            value = col[year_ago_idx]
        else:
            if year_ago_idx in col:
                value = col[year_ago_idx]

        return value

    def _pct_change(self, x, y):
        if isinstance(y, int) and y == 0:
            return self.default_value
        return x - y / y

    @staticmethod
    def _change(x, y):
        return x - y
