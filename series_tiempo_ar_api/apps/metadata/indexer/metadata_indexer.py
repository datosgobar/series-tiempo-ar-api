#! coding: utf-8
from __future__ import print_function

import logging
from elasticsearch.helpers import parallel_bulk

from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance

from . import strings

logging.getLogger(__name__)


class MetadataIndexer(object):

    def __init__(self, data_json):
        self.data_json = data_json
        self.elastic = ElasticInstance.get()

    def index(self):
        self.init_index()
        actions = self.scrap_datajson()

        self.index_actions(actions)

    def init_index(self):
        Field.init(using=self.elastic)

    def index_actions(self, actions):
        for success, info in parallel_bulk(self.elastic, actions):
            if not success:
                logging.info(strings.INDEXING_ERROR.format(info))

    def scrap_datajson(self):
        themes = self.get_themes(self.data_json['themeTaxonomy'])

        actions = []
        for field in self.data_json.get_fields(only_time_series=True):
            dataset = self.data_json.get_dataset(identifier=field['dataset_identifier'])

            doc = Field(
                title=field['title'],
                description=field['description'],
                id=field['id'],
                dataset_title=dataset['title'],
                dataset_source=dataset['source'],
                dataset_description=dataset['description'],
                theme_description=themes[dataset['theme'][0]]
            )
            actions.append(doc.to_dict(include_meta=True))
        return actions

    @staticmethod
    def get_themes(theme_taxonomy):
        themes = {}
        for theme in theme_taxonomy:
            themes[theme['id']] = theme['description']

        return themes
