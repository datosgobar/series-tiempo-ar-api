#! coding: utf-8
import logging
from functools import reduce

from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from django_datajsonar.models import Distribution

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.datajsonar_repositories.series_repository import SeriesRepository
from series_tiempo_ar_api.libs.indexing import strings
from series_tiempo_ar_api.libs.indexing.indexer.data_frame import get_distribution_time_index_periodicity, init_df

from .operations import process_column
from .index import tseries_index

logger = logging.getLogger(__name__)


class DistributionIndexer:
    def __init__(self, index: str):
        self.elastic: Elasticsearch = connections.get_connection()
        self.index_name = index
        self.index = tseries_index(index)

    def run(self, distribution):
        actions = self.generate_es_actions(distribution)

        if not actions:
            return

        for success, info in parallel_bulk(self.elastic, actions):
            if not success:
                logger.warning(strings.BULK_REQUEST_ERROR, info)

        self.update_distribution_indexation_metadata(distribution)

    def generate_es_actions(self, distribution):
        time_index = DistributionRepository(distribution).get_time_index_series()
        df = init_df(distribution, time_index)

        if not df.columns.any():
            logger.warning(strings.NO_SERIES,
                           distribution.identifier,
                           distribution.dataset.catalog.identifier)
            return []

        es_actions = [process_column(df[col], self.index_name) for col in list(df.columns)]

        # List flatten: si el resultado son múltiples listas las junto en una sola
        actions = reduce(lambda x, y: x + y, es_actions) if isinstance(es_actions[0], list) else es_actions
        self.add_catalog_keyword(actions, distribution)
        return actions

    def update_distribution_indexation_metadata(self, distribution):
        time_index = DistributionRepository(distribution).get_time_index_series()
        for field in SeriesRepository.get_present_series(distribution=distribution).exclude(id=time_index.id):
            field.enhanced_meta.update_or_create(key=meta_keys.AVAILABLE, value='true')
        # Cálculo de metadatos adicionales sobre cada serie
        distribution.enhanced_meta.update_or_create(key=meta_keys.PERIODICITY,
                                                    defaults={
                                                        'value': get_distribution_time_index_periodicity(time_index)})

    def add_catalog_keyword(self, actions, distribution):
        for action in actions:
            action['_source']['catalog'] = distribution.dataset.catalog.identifier

    def reindex(self, distribution: Distribution):
        self._delete_distribution_data(distribution)
        self.run(distribution)

    def _delete_distribution_data(self, distribution):
        fields_to_delete = list(
            SeriesRepository.get_present_series(distribution=distribution)
            .exclude(identifier=None)
            .values_list('identifier', flat=True)
        )
        for field in fields_to_delete:
            series_data = Search(using=self.elastic,
                                 index=self.index._name).params(conflicts='proceed').filter('term', series_id=field)
            series_data.delete()
