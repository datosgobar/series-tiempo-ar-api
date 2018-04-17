#! coding: utf-8
from __future__ import print_function

import logging
from elasticsearch.helpers import parallel_bulk

from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance

from . import strings

logger = logging.getLogger(__name__)


class MetadataIndexer(object):

    def __init__(self, data_json):
        self.data_json = data_json
        self.elastic = ElasticInstance.get()
        logger.info('Hosts de ES: %s', self.elastic.transport.hosts)

    def index(self):
        logger.info(u'Inicio de la indexación de metadatos')
        self.init_index()

        actions = self.scrap_datajson()

        self.index_actions(actions)
        logger.info(u'Fin de la indexación de metadatos')

    # noinspection PyProtectedMember
    def init_index(self):
        if self.elastic.indices.exists(Field._doc_type.index):
            self.elastic.indices.delete(Field._doc_type.index)
        Field.init(using=self.elastic)

    def index_actions(self, actions):
        for success, info in parallel_bulk(self.elastic, actions):
            if not success:
                logger.info(strings.INDEXING_ERROR, info)

    def scrap_datajson(self):
        themes = self.get_themes(self.data_json['themeTaxonomy'])
        datasets = {}
        actions = []
        for field in self.data_json.get_fields(only_time_series=True):
            dataset = datasets.setdefault(field['dataset_identifier'],
                                          self.get_dataset(identifier=field['dataset_identifier']))

            doc = Field(
                title=field.get('title'),
                description=field.get('description'),
                id=field.get('id'),
                units=field.get('units'),
                dataset_title=dataset.get('title'),
                dataset_source=dataset.get('source'),
                dataset_source_keyword=dataset.get('source'),
                dataset_description=dataset.get('description'),
                dataset_publisher_name=dataset.get('publisher', {}).get('name'),
                dataset_theme=themes.get(dataset.get('theme', [None])[0])
            )
            actions.append(doc.to_dict(include_meta=True))
        return actions

    def get_dataset(self, identifier):
        for dataset in self.data_json['dataset']:
            if dataset['identifier'] == identifier:
                return dataset
        raise ValueError(u'Identifier no encontrado: {}'.format(identifier))

    @staticmethod
    def get_themes(theme_taxonomy):
        themes = {}
        for theme in theme_taxonomy:
            themes[theme['id']] = theme['label']

        return themes
