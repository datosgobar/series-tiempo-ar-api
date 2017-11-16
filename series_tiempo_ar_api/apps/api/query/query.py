#! coding: utf-8
from collections import OrderedDict

from pandas import json

from series_tiempo_ar_api.apps.api.exceptions import CollapseError
from series_tiempo_ar_api.apps.api.helpers import get_periodicity_human_format
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.es_query import ESQuery, CollapseQuery


class Query(object):
    """Encapsula la query pedida por un usuario. Tiene dos componentes
    principales: la parte de datos obtenida haciendo llamadas a
    Elasticsearch, y los metadatos guardados en la base de datos
    relacional
    """
    def __init__(self):
        self.es_query = ESQuery()
        self.series_models = []
        self.metadata_config = constants.API_DEFAULT_VALUES[constants.PARAM_METADATA]

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

        return self.es_query.get_series_ids()

    def add_pagination(self, start, limit):
        return self.es_query.add_pagination(start, limit)

    def add_filter(self, start_date, end_date):
        return self.es_query.add_filter(start_date, end_date)

    def add_series(self, name, field_model,
                   rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]):
        periodicities = [
            get_periodicity_human_format(field.distribution.periodicity)
            for field in self.series_models
        ]

        self.series_models.append(field_model)

        series_periodicity = get_periodicity_human_format(
            field_model.distribution.periodicity)

        if periodicities and series_periodicity not in periodicities:
            # Hay varias series con distintas periodicities, colapso los datos
            periodicity = self.get_max_periodicity(periodicities)
            self.add_collapse(collapse=periodicity)

        self.es_query.add_series(name, rep_mode)

    @staticmethod
    def get_max_periodicity(periodicities):
        """Devuelve la periodicity máxima en la lista periodicities"""
        order = constants.COLLAPSE_INTERVALS
        index = 0
        for periodicity in periodicities:
            field_index = order.index(periodicity)
            index = index if index > field_index else field_index

        return order[index]

    def add_collapse(self, agg=None,
                     collapse=None):
        self._validate_collapse(collapse)
        self.es_query = CollapseQuery(self.es_query)
        self.es_query.add_collapse(agg, collapse)

    def set_metadata_config(self, how):
        self.metadata_config = how

    def _validate_collapse(self, collapse):
        order = constants.COLLAPSE_INTERVALS

        for serie in self.series_models:
            periodicity = serie.distribution.periodicity
            periodicity = get_periodicity_human_format(periodicity)
            if order.index(periodicity) > order.index(collapse):
                raise CollapseError

    def run(self):
        response = OrderedDict()  # Garantiza el orden de los objetos cargados
        if self.metadata_config != constants.METADATA_ONLY:
            response['data'] = self.es_query.run()

        if self.metadata_config != constants.METADATA_NONE:
            response['meta'] = self.get_metadata()

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

        metadata = None
        full_meta_values = (constants.METADATA_ONLY, constants.METADATA_FULL)
        if self.metadata_config in full_meta_values:
            metadata = self._get_full_metadata(serie_model)
        elif self.metadata_config == constants.METADATA_SIMPLE:
            metadata = self._get_simple_metadata(serie_model)
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
        """Devuelve la periodicidad de la o las series pedidas. Si son
        muchas devuelve el intervalo de tiempo colapsado
        """
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

    def _get_simple_metadata(self, serie_model):
        """Obtiene los campos de metadatos marcados como simples en
        la configuración de un modelo de una serie. La estructura
        final de metadatos respeta el formato de un data.json
        """

        # Idea: obtener todos los metadatos y descartar los que no queremos
        meta = self._get_full_metadata(serie_model)

        for meta_field in meta.keys():
            if meta_field not in constants.CATALOG_SIMPLE_META_FIELDS:
                meta.pop(meta_field)

        dataset = meta['dataset'][0]  # Dataset de un único elemento
        for meta_field in dataset.keys():
            if meta_field not in constants.DATASET_SIMPLE_META_FIELDS:
                dataset.pop(meta_field)

        distribution = dataset['distribution'][0]
        for meta_field in distribution.keys():
            if meta_field not in constants.DISTRIBUTION_SIMPLE_META_FIELDS:
                distribution.pop(meta_field)

        field = distribution['field'][0]
        for meta_field in field.keys():
            if meta_field not in constants.FIELD_SIMPLE_META_FIELDS:
                field.pop(meta_field)

        return meta
