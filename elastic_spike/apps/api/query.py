#! coding: utf-8

from django.conf import settings
from elasticsearch.client import Elasticsearch
from elasticsearch_dsl import Search, MultiSearch


class Query:
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""
    def __init__(self):
        """
        Instancia una nueva query

        args:
            series (str):  Nombre de una serie
            parameters (dict): Opciones de la query
        """
        self.series = []
        self.elastic = Elasticsearch()
        self.result = {}
        self.data = []

    def add_pagination(self, start, limit):
        if not len(self.series):
            self.series.append({'search': Search(using=self.elastic)})

        for serie in self.series:
            serie['search'] = serie['search'][start:limit]

    def add_filter(self, start, end):
        if not len(self.series):
            self.series.append({'search': Search(using=self.elastic)})

        _filter = {
            'lte': end,
            'gte': start
        }
        for serie in self.series:
            serie['search'] = serie['search'].filter('range',
                                                     timestamp=_filter)

    def add_series(self, series_id, rep_mode):
        if len(self.series) == 1:
            search = self.series[0]['search'].doc_type(id)
        else:
            search = Search(doc_type=series_id)

        self.series.append({
            'search': search,
            'rep_mode': rep_mode
        })

    def run(self):
        multi_search = MultiSearch(index=settings.TS_INDEX,
                                   using=self.elastic)

        for serie in self.series:
            multi_search = multi_search.add(serie['search'])

        responses = multi_search.execute()
        self.format_response(responses)

    def format_response(self, responses):
        for i, response in enumerate(responses):
            rep_mode = self.series[i]['rep_mode']
            self.populate_data(response, rep_mode)

    def populate_data(self, response, rep_mode):
        for i, hit in enumerate(response):
            if i == len(self.data):
                data_row = [hit.timestamp]
                self.data.append(data_row)
            self.data[i].append(hit[rep_mode])
