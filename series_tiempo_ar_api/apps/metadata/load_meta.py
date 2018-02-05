#!coding=utf8

import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from pydatajson import DataJson

mapping = """
{
  "mappings": {
    "doc": {
      "properties": {
        "description": {"type": "text"},
        "id": {"type": "keyword"},
        "title": {"type": "keyword"},
        "dataset_title": {"type": "text"},
        "dataset_source": {"type": "text"},
        "theme_description": {"type": "text"}
      }
    }
  }
}
"""

elastic = Elasticsearch(['elastic:changeme@localhost:9200'])

sspm = DataJson('http://infra.datos.gob.ar/catalog/sspm/data.json')

actions = []
theme_taxonomy = sspm['themeTaxonomy']

themes = {}
for theme in theme_taxonomy:
    themes[theme['id']] = theme['description']

action_template = {
    "_index": "metadata",
    "_type": "doc",
    "_id": None,
    "_source": {}
}

counter = 0
for field in sspm.get_fields():
    if field.get('specialType'):
        continue

    dataset = sspm.get_dataset(identifier=field['dataset_identifier'])
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

for success, info in parallel_bulk(elastic, actions):
    if not success:
        print(info)

search_body = """
{
  "query": {
    "fuzzy": {
      "_all": "pib"
    }
  }
}"""
print(json.dumps(elastic.search(index='metadata', body=search_body), indent=2))
