#!coding=utf8
import os
import csv

from django.conf import settings
from django_datajsonar.models import Field
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance
from elasticsearch.helpers import scan

from . import constants


def generate_values_csv():
    periodicities = {
        'year': 'R/P1Y',
        'quarter': 'R/P3M',
        'month': 'R/P1M',
        'day': 'R/P1D',
        'semseter': 'R/P6M'
    }

    filepath = os.path.join(settings.MEDIA_ROOT, constants.VALUES_CSV)
    fields = Field.objects.all().prefetch_related('distribution',
                                                  'distribution__dataset',
                                                  'distribution__dataset__catalog')
    fields_dict = {}

    for field in fields:
        fields_dict[field.identifier] = {
            'catalog': field.distribution.dataset.catalog.identifier,
            'dataset': field.distribution.dataset.identifier,
            'distribution': field.distribution.identifier,
        }

    client = ElasticInstance.get()
    with open(filepath, 'w') as f:
        writer = csv.writer(f)
        writer.writerow([  # Header
            'catalogo_id',
            'dataset_id',
            'distribucion_id',
            'serie_id',
            'indice_tiempo',
            'valor',
            'indice_tiempo_frecuencia'])

        query = {'query': {'match': {'raw_value': True}}}  # solo valores crudos
        for res in scan(client, index='indicators', query=query):
            source = res['_source']

            field = source['series_id']
            if field not in fields_dict:
                continue
            row = [fields_dict[field]['catalog'],
                   fields_dict[field]['dataset'],
                   fields_dict[field]['distribution'],
                   field,
                   source.get('timestamp'),
                   source.get('value'),
                   periodicities[source.get('interval')]]
            writer.writerow(row)
