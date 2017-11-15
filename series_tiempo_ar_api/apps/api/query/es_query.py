#! coding: utf-8
import iso8601
from django.conf import settings
from elasticsearch_dsl import Search, MultiSearch

from series_tiempo_ar_api.apps.api.exceptions import QueryError
from series_tiempo_ar_api.apps.api.helpers import find_index, get_relative_delta
from series_tiempo_ar_api.apps.api.query.elastic import ElasticInstance
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.query import constants


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
            'start': constants.API_DEFAULT_VALUES['start'],
            'limit': constants.API_DEFAULT_VALUES['limit'],
            'sort': constants.API_DEFAULT_VALUES['sort']
        }

    def add_pagination(self, start, limit):
        if not len(self.series):
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        for serie in self.series:
            serie.search = serie.search[start:limit]

        # Guardo estos parámetros, necesarios en el evento de hacer un collapse
        self.args[constants.PARAM_START] = start
        self.args[constants.PARAM_LIMIT] = limit

    def add_filter(self, start=None, end=None):
        if not len(self.series):
            raise QueryError(strings.EMPTY_QUERY_ERROR)

        _filter = {
            'lte': end,
            'gte': start
        }
        for serie in self.series:
            serie.search = serie.search.filter('range',
                                               timestamp=_filter)

    def add_series(self,
                   series_id,
                   rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]):
        self._init_series(series_id, rep_mode)

    def run(self):
        if not self.series:
            raise QueryError(strings.EMPTY_QUERY_ERROR)

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
            rep_mode = self.series[i].rep_mode
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
                     rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]):

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
        if not self.data:
            return {}

        return {
            constants.PARAM_START_DATE: self.data[0][0],
            constants.PARAM_END_DATE: self.data[-1][0]
        }

    def sort(self, how):
        """Ordena los resultados por ascendiente o descendiente"""
        if how == constants.SORT_ASCENDING:
            order = 'timestamp'

        elif how == constants.SORT_DESCENDING:
            order = '-timestamp'
        else:
            msg = strings.INVALID_SORT_PARAMETER.format(how)
            raise ValueError(msg)

        for serie in self.series:
            serie.search = serie.search.sort(order)

        # Guardo el parámetro, necesario en el evento de hacer un collapse
        self.args[constants.PARAM_SORT] = how


class CollapseQuery(ESQuery):
    """Calcula el promedio de una serie en base a una bucket
    aggregation
    """

    def __init__(self, other=None):
        super(CollapseQuery, self).__init__()
        # Datos guardados en la instancia para asegurar conmutabilidad
        # de operaciones
        self.collapse_aggregation = \
            constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]
        self.collapse_interval = constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE]

        if other:
            self.series = list(other.series)
            self.args = other.args.copy()
            # Inicializo con collapse default a las series
            self.add_collapse()

    def add_series(self,
                   series_id,
                   rep_mode=constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]):
        super(CollapseQuery, self).add_series(series_id, rep_mode)
        # Instancio agregación de collapse con parámetros default
        serie = self.series[-1]
        search = serie.search
        serie.search = self._add_aggregation(search, rep_mode)

    def add_collapse(self, agg=None, interval=None):
        if agg:
            self.collapse_aggregation = agg
        if interval:
            # Temporalmente: convertir collapse semestral en anual,
            # Elasticsearch no los soporta
            if interval == 'semester':
                interval = 'year'

            self.collapse_interval = interval

        for serie in self.series:
            rep_mode = serie.rep_mode
            search = serie.search
            serie.search = self._add_aggregation(search, rep_mode)

    def _add_aggregation(self, search, rep_mode):
        search = search[:0]
        search.aggs \
            .bucket('agg',
                    'date_histogram',
                    field='timestamp',
                    order={"_key": self.args[constants.PARAM_SORT]},
                    interval=self.collapse_interval) \
            .metric('agg',
                    self.collapse_aggregation,
                    field=rep_mode)

        return search

    def _format_single_response(self, row_len, response, start, limit):
        if not response.aggregations:
            return

        hits = response.aggregations.agg.buckets

        first_date = self._format_timestamp(hits[0]['key_as_string'])

        # Agrego rows necesarios vacíos para garantizar continuidad
        self._make_date_index_continuous(first_date)

        start_index = find_index(self.data, first_date)
        if start_index < 0:
            start_index = 0  # Se va a appendear, no uso el offset

        for i, hit in enumerate(hits):
            if i < start:
                continue
            data_index = i - start

            if data_index >= limit:  # Ya conseguimos datos suficientes
                break
            if data_index + start_index == len(self.data):  # No hay row, inicializo
                # Strip de la parte de tiempo del datetime
                timestamp = hit['key_as_string']
                data_row = [self._format_timestamp(timestamp)]
                if row_len > 2:  # Lleno el row de nulls
                    nulls = [None for _ in range(1, len(self.data[0]))]
                    data_row.extend(nulls)
                self.data.append(data_row)

            self.data[data_index + start_index].append(hit['agg'].value)

        self._fill_nulls(row_len)

    def _format_response(self, responses):
        start = self.args.get(constants.PARAM_START)
        limit = self.args.get(constants.PARAM_LIMIT)

        self._sort_responses(responses)

        for row_len, response in enumerate(responses, 2):
            # Smart solution
            self._format_single_response(row_len, response, start, limit)

    @staticmethod
    def _sort_responses(responses):
        def list_len_cmp(x, y):
            """Ordena por primera fecha de resultados"""
            if not x or not y:
                return 0

            first_date_x = x[0].timestamp
            first_date_y = y[0].timestamp
            if first_date_x == first_date_y:
                return 0

            if first_date_x < first_date_y:
                return -1
            return 1

        responses.sort(list_len_cmp)

    def _fill_nulls(self, row_len):
        """Rellena los espacios faltantes de la respuesta, haciendo
        continuo el índice de tiempo y rellenando con nulls los datos
        faltantes hasta que toda fila tenga longitud 'row_len'
        """
        for row in self.data:
            while len(row) < row_len:
                row.append(None)

    def _make_date_index_continuous(self, date_up_to):
        """Hace el índice de tiempo de los resultados continuo (según
        el intervalo de resultados), sin saltos, hasta la fecha
        especificada
        """

        # Si no hay datos cargados no hay nada que hacer
        if not len(self.data):
            return

        end_date = iso8601.parse_date(date_up_to)
        last_date = iso8601.parse_date(self.data[-1][0])
        delta = get_relative_delta(self.collapse_interval)
        row_len = len(self.data[0])
        while last_date < end_date:
            last_date = last_date + delta
            date_str = self._format_timestamp(str(last_date.date()))
            row = [date_str]
            row.extend([None for _ in range(1, row_len)])
            self.data.append(row)


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
