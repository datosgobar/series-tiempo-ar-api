#! coding: utf-8
from datetime import datetime

from django.conf import settings
from elasticsearch_dsl import Search, Q, A

from series_tiempo_ar_api.apps.api.helpers import extra_offset
from series_tiempo_ar_api.apps.api.query import constants, strings
from series_tiempo_ar_api.apps.api.query.es_query.periods_between import periods_between


class Series:
    def __init__(self, index, series_id, rep_mode, periodicity, collapse_agg=None):
        self.index = index
        self.series_id = series_id
        self.rep_mode = rep_mode
        self.original_periodicity = periodicity
        self.periodicity = periodicity
        self.collapse_agg = collapse_agg or constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]
        self._search = self._init_search()

    def _init_search(self):
        search = Search(index=self.index)

        search = search.sort(settings.TS_TIME_INDEX_FIELD)  # Default: ascending sort
        search = search.filter('bool', must=[Q('match', series_id=self.series_id)])
        return search

    def add_range_filter(self, start, end):
        _filter = {
            'lte': end,
            'gte': start
        }
        self._search = self._search.filter('range', timestamp=_filter)

    def add_collapse(self, periodicity):
        if self.collapse_agg not in constants.IN_MEMORY_AGGS:
            self._search = self.search.filter('bool', must=[Q('match', interval=periodicity)])

        elif periodicity != self.original_periodicity:
            # Agregamos la aggregation (?) para que se ejecute en ES en runtime
            self.search.aggs.bucket('test',
                                    A('date_histogram',
                                      field='timestamp',
                                      interval=periodicity,
                                      format='yyyy-MM-dd').
                                    metric('test', self.collapse_agg, field=self.rep_mode))
        else:  # Ignoramos la in memory ag
            self.collapse_agg = constants.AGG_DEFAULT
            self._search = self.search.filter('bool', must=[Q('match', interval=periodicity)])

        self.periodicity = periodicity

    def add_pagination(self, start, limit, request_start_dates=None):
        # ☢️☢️☢️
        es_start = self.get_es_start(request_start_dates, start)

        es_offset = start + limit
        if self.rep_mode != constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE]:
            es_offset += extra_offset(self.periodicity)

        self._search = self._search[es_start:es_offset]

    def get_es_start(self, request_start_dates, start):
        """Calcula el comienzo de la query para esta serie particular. El parámetro
        'start' pasado es el primer valor a devolver del resultado global, conformado por
        todas las series pedidas. Si una serie individual comienza en una fecha posterior al
        resultado global, el slicing de la búsqueda de ES con el parámetro start directo quitaría
        valores adicionales a los esperados. Debemos ajustar ese valor por la cantidad de períodos
        de diferencia entre el primer valor de la serie, y el comienzo del resultado (la menor
        fecha de todas las series pedidas)
        """
        min_date = min(request_start_dates.values()) if request_start_dates else None
        start_date = request_start_dates.get(self.series_id) if request_start_dates else None
        es_start = start - self.serie_first_date_offset(start_date,
                                                        min_date)
        es_start = max(es_start, 0)
        return es_start

    def serie_first_date_offset(self, series_start_date: datetime, min_start_date: datetime):
        if series_start_date is None or min_start_date is None:
            return 0

        return periods_between(series_start_date, min_start_date, self.periodicity)

    def sort(self, how):
        if how == constants.SORT_ASCENDING:
            order = settings.TS_TIME_INDEX_FIELD

        elif how == constants.SORT_DESCENDING:
            order = '-' + settings.TS_TIME_INDEX_FIELD
        else:
            msg = strings.INVALID_SORT_PARAMETER.format(how)
            raise ValueError(msg)

        self._search = self._search.sort(order)

    @property
    def search(self):
        self._add_collapse()
        self._add_collapse_agg()
        return self._search

    def _add_collapse(self):
        if self.collapse_agg not in constants.IN_MEMORY_AGGS:
            self._search = self._search.filter('bool', must=[Q('match', interval=self.periodicity)])

        elif self.periodicity != self.original_periodicity:
            # Agregamos la aggregation (?) para que se ejecute en ES en runtime
            self._search.aggs.bucket('test',
                                     A('date_histogram',
                                       field='timestamp',
                                       interval=self.periodicity,
                                       format='yyyy-MM-dd').
                                     metric('test', self.collapse_agg, field=self.rep_mode))
        else:  # Ignoramos la in memory ag
            self.collapse_agg = constants.AGG_DEFAULT
            self._search = self._search.filter('bool', must=[Q('match', interval=self.periodicity)])

    def _add_collapse_agg(self):
        # Filtra los resultados por la serie pedida. Si se hace en memoria filtramos
        # por la agg default, y calculamos la agg pedida en runtime
        agg = self.collapse_agg if self.collapse_agg not in constants.IN_MEMORY_AGGS else constants.AGG_DEFAULT
        self._search = self._search.filter('bool',
                                           must=[Q('match', aggregation=agg)])
