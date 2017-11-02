#! coding: utf-8
from collections import OrderedDict

from django.conf import settings
from pandas import json

from series_tiempo_ar_api.apps.api.helpers import get_periodicity_human_format
from series_tiempo_ar_api.apps.api.query.es_query import ESQuery, CollapseQuery
from series_tiempo_ar_api.apps.api.query.exceptions import CollapseError


class Query(object):
    """Encapsula la query pedida por un usuario. Tiene dos componentes
    principales: la parte de datos obtenida haciendo llamadas a
    Elasticsearch, y los metadatos guardados en la base de datos
    relacional
    """
    def __init__(self):
        self.es_query = ESQuery()
        self.series_models = []
        self.meta = {}
        self.metadata_config = settings.API_DEFAULT_VALUES['metadata']

    def get_series_ids(self):
        return self.es_query.get_series_ids()

    def add_pagination(self, start, limit):
        return self.es_query.add_pagination(start, limit)

    def add_filter(self, start_date, end_date):
        return self.es_query.add_filter(start_date, end_date)

    def add_series(self, name, field,
                   rep_mode=settings.API_DEFAULT_VALUES['rep_mode']):
        self.series_models.append(field)
        return self.es_query.add_series(name, rep_mode)

    def add_collapse(self, agg=None,
                     collapse=None,
                     rep_mode=settings.API_DEFAULT_VALUES['rep_mode']):
        self._validate_collapse(collapse)
        self.es_query = CollapseQuery(self.es_query)
        return self.es_query.add_collapse(agg, collapse, rep_mode)

    def set_metadata_config(self, how):
        self.metadata_config = how

    def _validate_collapse(self, collapse):
        order = ['day', 'month', 'quarter', 'year']

        for serie in self.series_models:
            periodicity = serie.distribution.periodicity
            periodicity = get_periodicity_human_format(periodicity)
            if order.index(periodicity) > order.index(collapse):
                raise CollapseError

    def run(self):
        response = OrderedDict()
        if self.metadata_config != 'only':
            response['data'] = self.es_query.run()

        if self.metadata_config in ('full', 'only'):
            response['meta'] = self.get_metadata()

        return response

    def get_metadata(self):
        if self.metadata_config == 'none':
            return None

        meta = []
        index_meta = {
            'frequency': self._calculate_data_frequency()
        }
        if self.metadata_config != 'only':
            index_meta.update(self.es_query.get_data_start_end_dates())

        meta.append(index_meta)
        for serie_model in self.series_models:
            meta.append(self._get_series_metadata(serie_model))

        return meta

    def _get_series_metadata(self, serie_model):
        """Devuelve un diccionario (data.json-like) de los metadatos
        de la serie:

        {
            <catalog_meta>
            "dataset": [
                <dataset_meta>
                "distribution": [
                    <distribution_meta>
                    "field": [
                        <field_meta>
                    ]
                ]
            ]
        }

        """

        if self.meta:
            return self.meta

        metadata = None
        if self.metadata_config == 'full' or self.metadata_config == 'only':
            metadata = self._get_full_metadata(serie_model)

        self.meta = metadata  # "Cacheado"
        return metadata

    @staticmethod
    def _get_full_metadata(field):
        distribution = field.distribution
        dataset = distribution.dataset
        catalog = dataset.catalog
        metadata = json.loads(catalog.metadata)
        dataset_meta = json.loads(dataset.metadata)
        distribution_meta = json.loads(distribution.metadata)
        field_meta = json.loads(field.metadata)
        distribution_meta['field'] = [field_meta]
        dataset_meta['distribution'] = [distribution_meta]
        metadata['dataset'] = [dataset_meta]
        return metadata

    def _calculate_data_frequency(self):
        if hasattr(self.es_query, 'collapse_interval'):
            # noinspection PyUnresolvedReferences
            return self.es_query.collapse_interval
        else:
            periodicity = self.series_models[0].distribution.periodicity
            return get_periodicity_human_format(periodicity)

    def sort(self, how):
        return self.es_query.sort(how)

    def get_series_identifiers(self):
        """Devuelve los identifiers a nivel dataset, distribution
        y field de cada una de las series cargadas en la query
        """

        result = []
        for field in self.series_models:
            result.append({
                'id': field.series_id,
                'distribution': field.distribution.identifier,
                'dataset': field.distribution.dataset.identifier
            })
        return result
