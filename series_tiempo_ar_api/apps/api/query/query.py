#! coding: utf-8
import json
from collections import OrderedDict
from typing import Union

from django.conf import settings
from django_datajsonar.models import Catalog, Dataset, Distribution, Field
from iso8601 import iso8601

from series_tiempo_ar_api.apps.api.exceptions import CollapseError
from series_tiempo_ar_api.apps.api.helpers import get_periodicity_human_format
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.metadata_response import MetadataResponse
from series_tiempo_ar_api.apps.management import meta_keys
from .es_query.es_query import ESQuery

datajson_entity = Union[Catalog, Dataset, Distribution, Field]


class Query(object):
    """Encapsula la query pedida por un usuario. Tiene dos componentes
    principales: la parte de datos obtenida haciendo llamadas a
    Elasticsearch, y los metadatos guardados en la base de datos
    relacional
    """
    def __init__(self, index=settings.TS_INDEX):
        self.es_index = index
        self.es_query = ESQuery(index)
        self.series_models = []
        self.metadata_config = constants.API_DEFAULT_VALUES[constants.PARAM_METADATA]
        self.metadata_flatten = False

    def get_series_ids(self, how=constants.API_DEFAULT_VALUES[constants.PARAM_HEADER]):
        """Devuelve una lista con strings que identifican a las series
        de tiempo cargadas, según el parámetro 'how':
            - 'names': los nombres (títulos) de las series
            - 'ids': las IDs de las series
        """
        if how and how not in constants.VALID_CSV_HEADER_VALUES:
            raise ValueError

        if how == constants.HEADER_PARAM_NAMES:
            return [model.title for model in self.series_models]

        if how == constants.HEADER_PARAM_DESCRIPTIONS:
            return [json.loads(model.metadata).get('description', '') for model in self.series_models]

        return self.es_query.get_series_ids()

    def add_pagination(self, start, limit):
        start_dates = {serie.identifier: meta_keys.get(serie, meta_keys.INDEX_START) for serie in self.series_models}
        start_dates = {k: iso8601.parse_date(v) if v is not None else None for k, v in start_dates.items()}
        return self.es_query.add_pagination(start, limit, start_dates=start_dates)

    def add_filter(self, start_date, end_date):
        return self.es_query.add_filter(start_date, end_date)

    def add_series(self, name, field_model,
                   rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE],
                   collapse_agg=constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]):
        periodicities = [
            get_periodicity_human_format(
                field.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value)
            for field in self.series_models
        ]

        self.series_models.append(field_model)

        series_periodicity = get_periodicity_human_format(
            field_model.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value)

        periodicity = get_periodicity_human_format(
            field_model.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value)
        if periodicities and series_periodicity not in periodicities:
            # Hay varias series con distintas periodicities, colapso los datos
            periodicities.append(series_periodicity)
            periodicity = self.get_max_periodicity(periodicities)
            self.add_collapse(collapse=periodicity)

        self.es_query.add_series(name, rep_mode, periodicity, collapse_agg)

    @staticmethod
    def get_max_periodicity(periodicities):
        """Devuelve la periodicity máxima en la lista periodicities"""
        order = constants.COLLAPSE_INTERVALS
        index = 0
        for periodicity in periodicities:
            field_index = order.index(periodicity)
            index = index if index > field_index else field_index

        return order[index]

    def add_collapse(self, collapse=None):
        self._validate_collapse(collapse)
        self.es_query.add_collapse(collapse)

    def set_metadata_config(self, how):
        self.metadata_config = how

    def _validate_collapse(self, collapse):
        order = constants.COLLAPSE_INTERVALS

        for serie in self.series_models:
            periodicity = serie.distribution.enhanced_meta.get(key=meta_keys.PERIODICITY).value
            periodicity = get_periodicity_human_format(periodicity)
            if order.index(periodicity) > order.index(collapse):
                raise CollapseError

    def run(self):
        response = OrderedDict()  # Garantiza el orden de los objetos cargados
        self.es_query.run()
        if self.metadata_config != constants.METADATA_ONLY:
            response['data'] = self.es_query.get_results_data()

        if self.metadata_config != constants.METADATA_NONE:
            response['meta'] = self.get_metadata()

        response['count'] = self.es_query.get_results_count()
        return response

    def get_metadata(self):
        """Arma la respuesta de metadatos: una lista de objetos con
        un metadato por serie de tiempo pedida, más una extra para el
        índice de tiempo
        """
        if self.metadata_config == constants.METADATA_NONE:
            return None

        meta = []
        index_meta = {
            'frequency': self._calculate_data_frequency()
        }
        # si pedimos solo metadatos no tenemos start y end dates
        if self.metadata_config != constants.METADATA_ONLY:
            index_meta.update(self.es_query.get_data_start_end_dates())

        meta.append(index_meta)
        for serie_model in self.series_models:
            meta.append(self._get_series_metadata(serie_model))

        return meta

    def _get_series_metadata(self, serie_model):
        """Devuelve un diccionario (data.json-like) de los metadatos
        de la serie:

        {
            "catalog": [<catalog_meta>],
            "dataset": [<dataset_meta>],
            "distribution": [<distribution_meta>],
            "field": [<field_meta>],
        }

        Si está seteado el flag self.metadata_flatten, aplana la respuesta:
        {
            catalog_meta1: ...,
            catalog_meta2: ...,
            dataset_meta1: ...,
            <nivel>_<meta_key>: <meta_value>
            ...
        }
        """
        simple_meta = self.metadata_config == constants.METADATA_SIMPLE
        meta_response = MetadataResponse(serie_model, simple=simple_meta, flat=self.metadata_flatten)

        return meta_response.get_response()

    def _calculate_data_frequency(self):
        """Devuelve la periodicidad de la o las series pedidas. Si son
        muchas devuelve el intervalo de tiempo colapsado
        """
        return self.es_query.args[constants.PARAM_PERIODICITY]

    def sort(self, how):
        return self.es_query.sort(how)

    def get_series_identifiers(self):
        """Devuelve los identifiers a nivel dataset, distribution
        y field de cada una de las series cargadas en la query
        """

        result = []
        for field in self.series_models:
            result.append({
                'id': field.identifier,
                'distribution': field.distribution.identifier,
                'dataset': field.distribution.dataset.identifier
            })
        return result

    def flatten_metadata_response(self):
        self.metadata_flatten = True

    def reverse(self):
        self.es_query.reverse()
