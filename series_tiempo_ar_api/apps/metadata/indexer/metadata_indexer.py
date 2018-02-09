#! coding: utf-8
from __future__ import print_function

from elasticsearch.helpers import parallel_bulk
from pydatajson import DataJson

from series_tiempo_ar_api.apps.metadata.indexer.doc_types import Field
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class MetadataIndexer(object):

    def __init__(self):
        self.elastic = ElasticInstance.get()

    def index(self, datajson_url):
        self.init_index()
        data_json = DataJson(datajson_url)
        actions = self.scrap_datajson(data_json)

        self.index_actions(actions)

    def init_index(self):
        Field.init(using=self.elastic)

    @staticmethod
    def index_actions(actions):
        elastic = ElasticInstance.get()
        for success, info in parallel_bulk(elastic, actions):
            if not success:
                print(info)

    def scrap_datajson(self, data_json):
        themes = self.get_themes(data_json['themeTaxonomy'])

        actions = []
        for field in data_json.get_fields():
            if field.get('specialType'):
                continue

            dataset = data_json.get_dataset(identifier=field['dataset_identifier'])

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
