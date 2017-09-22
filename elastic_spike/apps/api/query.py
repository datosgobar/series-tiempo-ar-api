#! coding: utf-8

from django.conf import settings
from elasticsearch.client import Elasticsearch
from elasticsearch_dsl import Search, MultiSearch


class Query(object):
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
        self.data = []
        self.args = {}

    def add_pagination(self, start, limit):
        if not len(self.series):
            self._init_series()

        for serie in self.series:
            serie['search'] = serie['search'][start:limit]

        # Guardo estos parámetros, necesarios en el evento de hacer un collapse
        self.args['start'] = start
        self.args['limit'] = limit

    def add_filter(self, start, end):
        if not len(self.series):
            self._init_series()

        _filter = {
            'lte': end,
            'gte': start
        }
        for serie in self.series:
            serie['search'] = serie['search'].filter('range',
                                                     timestamp=_filter)

    def add_series(self, series_id, rep_mode):
        if len(self.series) == 1:
            search = self.series[0]['search'].doc_type(series_id)
        else:
            search = Search(doc_type=series_id).sort('timestamp')

        self.series.append({
            'search': search,
            'rep_mode': rep_mode
        })

    def run(self):
        if not self.series:
            self._init_series()

        multi_search = MultiSearch(index=settings.TS_INDEX,
                                   using=self.elastic)

        for serie in self.series:
            search = serie.get('search')
            multi_search = multi_search.add(search)

        responses = multi_search.execute()
        self._format_response(responses)

    def _format_response(self, responses):
        for i, response in enumerate(responses):
            rep_mode = self.series[i]['rep_mode']
            self._populate_data(response, rep_mode)

    def _populate_data(self, response, rep_mode):
        for i, hit in enumerate(response):
            if i == len(self.data):
                data_row = [hit.timestamp]
                self.data.append(data_row)
            self.data[i].append(hit[rep_mode])

    def _init_series(self):
        self.series.append({
            'search': Search(using=self.elastic).sort('timestamp'),
            'rep_mode': settings.API_DEFAULT_VALUES['rep_mode']
        })


class CollapseQuery(Query):
    """Calcula el promedio de una serie en base a una bucket
    aggregation
    """
    def __init__(self, other=None):
        Query.__init__(self)
        # Datos guardados en la instancia para asegurar conmutabilidad
        # de operaciones
        self.collapse_aggregation = \
            settings.API_DEFAULT_VALUES['collapse_aggregation']
        self.collapse = settings.API_DEFAULT_VALUES['collapse']

        if other:
            self.series = list(other.series)
            self.args = other.args.copy()

    def add_series(self, series_id, rep_mode):
        Query.add_series(self, series_id, rep_mode)
        # Instancio agregación de collapse con parámetros default
        serie = self.series[-1]
        search = serie['search']
        serie['search'] = self._add_aggregation(search, rep_mode)

    def add_collapse(self, agg=None, interval=None, global_rep_mode=None):
        if agg:
            self.collapse_aggregation = agg
        if interval:
            self.collapse = interval

        for serie in self.series:
            rep_mode = serie.get('rep_mode', global_rep_mode)
            search = serie['search']
            serie['search'] = self._add_aggregation(search, rep_mode)

    def _add_aggregation(self, search, rep_mode):
        search = search[:0]
        search.aggs \
            .bucket('agg',
                    'date_histogram',
                    field='timestamp',
                    interval=self.collapse) \
            .metric('agg',
                    self.collapse_aggregation,
                    field=rep_mode)

        return search

    def _format_response(self, responses):

        start = self.args.get('start', settings.API_DEFAULT_VALUES['start'])
        limit = self.args.get('limit',
                              start + settings.API_DEFAULT_VALUES['limit'])
        for response in responses:
            if not response.aggregations:
                continue

            hits = response.aggregations.agg.buckets

            # Este loop DEBE ser de esta forma: 'hits' no es una lista común
            # Entonces declarar el offset en enumerate no tiene el resultado
            # esperado de saltearse los primeros 'start' índices
            for i, hit in enumerate(hits):
                if i < start:
                    continue

                if i - start >= limit or i >= len(hits):  # No hay más datos
                    break
                if i - start == len(self.data):  # No hay row, inicializo
                    data_row = [hit['key_as_string']]
                    self.data.append(data_row)

                self.data[i - start].append(hit['agg'].value)
