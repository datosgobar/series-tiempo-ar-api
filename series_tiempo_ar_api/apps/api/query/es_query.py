#! coding: utf-8
from django.conf import settings
from elasticsearch_dsl import Search, MultiSearch

from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance


class ESQuery(object):
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
        self.elastic = ElasticInstance()
        self.data = []

        # Parámetros que deben ser guardados y accedidos varias veces
        self.args = {
            'start': settings.API_DEFAULT_VALUES['start'],
            'limit': settings.API_DEFAULT_VALUES['limit'],
            'sort': settings.API_DEFAULT_VALUES['sort']
        }

    def add_pagination(self, start, limit):
        if not len(self.series):
            self._init_series()

        for serie in self.series:
            serie.search = serie.search[start:limit]

        # Guardo estos parámetros, necesarios en el evento de hacer un collapse
        self.args['start'] = start
        self.args['limit'] = limit

    def add_filter(self, start=None, end=None):
        if not len(self.series):
            self._init_series()

        _filter = {
            'lte': end,
            'gte': start
        }
        for serie in self.series:
            serie.search = serie.search.filter('range',
                                               timestamp=_filter)

    def add_series(self,
                   series_id,
                   rep_mode=settings.API_DEFAULT_VALUES['rep_mode']):
        if len(self.series) == 1 and not self.series[0].series_id:
            search = self.series[0].search.filter('match',
                                                  series_id=series_id)

            self.series[0] = Series(series_id=series_id,
                                    rep_mode=rep_mode,
                                    search=search)
        else:
            self._init_series(series_id, rep_mode)

    def run(self):
        if not self.series:
            self._init_series()

        multi_search = MultiSearch(index=settings.TS_INDEX,
                                   doc_type=settings.TS_DOC_TYPE,
                                   using=self.elastic)

        for serie in self.series:
            search = serie.search
            multi_search = multi_search.add(search)

        responses = multi_search.execute()
        self._format_response(responses)
        return self.data

    def _format_response(self, responses):
        for i, response in enumerate(responses):
            rep_mode = self.series[i]['rep_mode']
            self._populate_data(response, rep_mode)

    def _populate_data(self, response, rep_mode):
        for i, hit in enumerate(response):
            if i == len(self.data):

                data_row = [self._format_timestamp(hit.timestamp)]
                self.data.append(data_row)

            if rep_mode in hit:
                self.data[i].append(hit[rep_mode])
            else:
                self.data[i].append(None)

    def _init_series(self, series_id=None,
                     rep_mode=settings.API_DEFAULT_VALUES['rep_mode']):

        search = Search(using=self.elastic)
        if series_id:
            search = search.filter('match', series_id=series_id)

        self.series.append(Series(series_id=series_id,
                                  rep_mode=rep_mode,
                                  search=search))

    @staticmethod
    def _format_timestamp(timestamp):
        if timestamp.find('T') != -1:  # Borrado de la parte de tiempo
            return timestamp[:timestamp.find('T')]
        return timestamp

    def get_series_ids(self):
        """Devuelve una lista de series cargadas"""
        return [serie.series_id for serie in self.series]

    def get_data_start_end_dates(self):
        return {
            'start_date': self.data[0][0],
            'end_date': self.data[-1][0]
        }

    def sort(self, how):
        """Ordena los resultados por ascendiente o descendiente"""
        if how == 'asc':
            order = 'timestamp'

        elif how == 'desc':
            order = '-timestamp'
        else:
            msg = '"how" debe ser "asc", o "desc", recibido {}'.format(how)
            raise ValueError(msg)

        for serie in self.series:
            serie.search = serie.search.sort(order)

        # Guardo el parámetro, necesario en el evento de hacer un collapse
        self.args['sort'] = how


class CollapseQuery(ESQuery):
    """Calcula el promedio de una serie en base a una bucket
    aggregation
    """

    def __init__(self, other=None):
        super(CollapseQuery, self).__init__()
        # Datos guardados en la instancia para asegurar conmutabilidad
        # de operaciones
        self.collapse_aggregation = \
            settings.API_DEFAULT_VALUES['collapse_aggregation']
        self.collapse_interval = settings.API_DEFAULT_VALUES['collapse']

        if other:
            self.series = list(other.series)
            self.args = other.args.copy()

    def add_series(self,
                   series_id,
                   rep_mode=settings.API_DEFAULT_VALUES['rep_mode']):
        ESQuery.add_series(self, series_id, rep_mode)
        # Instancio agregación de collapse con parámetros default
        serie = self.series[-1]
        search = serie.search
        serie.search = self._add_aggregation(search, rep_mode)

    def add_collapse(self, agg=None, interval=None, global_rep_mode=None):

        if agg:
            self.collapse_aggregation = agg
        if interval:
            self.collapse_interval = interval

        for serie in self.series:
            rep_mode = serie.get('rep_mode', global_rep_mode)
            search = serie.search
            serie.search = self._add_aggregation(search, rep_mode)

    def _add_aggregation(self, search, rep_mode):
        search = search[:0]
        search.aggs \
            .bucket('agg',
                    'date_histogram',
                    field='timestamp',
                    order={"_key": self.args['sort']},
                    interval=self.collapse_interval) \
            .metric('agg',
                    self.collapse_aggregation,
                    field=rep_mode)

        return search

    def _format_response(self, responses):

        start = self.args.get('start')
        limit = self.args.get('limit')
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
                    # Strip de la parte de tiempo del datetime
                    timestamp = hit['key_as_string']
                    data_row = [self._format_timestamp(timestamp)]
                    self.data.append(data_row)

                self.data[i - start].append(hit['agg'].value)

    def _calculate_data_frequency(self):
        return self.collapse_interval


class Series(object):

    def __init__(self, series_id=None, rep_mode=None, search=None):
        self.series_id = series_id
        self.rep_mode = rep_mode
        self.search = search or Search()
        self.meta = None

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def get(self, item, default=None):
        return getattr(self, item, default)
