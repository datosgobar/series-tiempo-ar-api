#! coding: utf-8
from __future__ import print_function

from elasticsearch.helpers import parallel_bulk
from pydatajson import DataJson

from . import constants
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
        if not self.elastic.indices.exists(constants.FIELDS_INDEX):
            self.elastic.indices.create(constants.FIELDS_INDEX, body=constants.FIELDS_MAPPING)

    @staticmethod
    def index_actions(actions):
        elastic = ElasticInstance.get()
        for success, info in parallel_bulk(elastic, actions):
            if not success:
                print(info)

    def scrap_datajson(self, data_json):
        themes = self.get_themes(data_json['themeTaxonomy'])

        action_template = {
            "_index": constants.FIELDS_INDEX,
            "_type": constants.FIELDS_DOC_TYPE,
            "_id": None,
            "_source": {}
        }
        actions = []
        counter = 0
        for field in data_json.get_fields():
            if field.get('specialType'):
                continue

            dataset = data_json.get_dataset(identifier=field['dataset_identifier'])
            action = action_template.copy()
            action['_source'] = {
                "title": field['title'],
                "description": field['description'] or "",
                "id": field['id'],
                'dataset_source': dataset['source'],
                'dataset_title': dataset['title'],
                'dataset_description': dataset['description'],
                'theme_description': themes[dataset['theme'][0]],
            }
            counter += 1
            action['_id'] = counter
            actions.append(action)
        return actions

    @staticmethod
    def get_themes(theme_taxonomy):
        themes = {}
        for theme in theme_taxonomy:
            themes[theme['id']] = theme['description']

        return themes
