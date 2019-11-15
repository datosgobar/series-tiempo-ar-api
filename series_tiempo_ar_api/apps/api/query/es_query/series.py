#! coding: utf-8
from datetime import datetime

from django.conf import settings
from elasticsearch_dsl import Search, Q, A

from series_tiempo_ar_api.apps.api.helpers import extra_offset
from series_tiempo_ar_api.apps.api.query import constants, strings
from series_tiempo_ar_api.apps.api.query.es_query.periods_between import periods_between


class Serie:
    """Patrón Builder sobre una query de Elasticsearch"""
    def __init__(self, index, series_id, rep_mode, periodicity, collapse_agg=None):
        self.index = index
        self.series_id = series_id
        self.rep_mode = rep_mode
        self.original_periodicity = periodicity
        self.periodicity = periodicity
        self.collapse_agg = collapse_agg or constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]

        self._search = None
        self.search_options = {
            constants.PARAM_START: constants.API_DEFAULT_VALUES[constants.PARAM_START],
            constants.PARAM_LIMIT: constants.API_DEFAULT_VALUES[constants.PARAM_LIMIT],
            constants.PARAM_START_DATE: None,
            constants.PARAM_END_DATE: None,
            constants.PARAM_SORT: settings.TS_TIME_INDEX_FIELD,  # Sort ascendiente por key
        }

    def _init_search(self):
        search = Search(index=self.index)

        search = search.sort(settings.TS_TIME_INDEX_FIELD)  # Default: ascending sort
        search = search.filter('bool', must=[Q('match', series_id=self.series_id)])
        return search

    def add_range_filter(self, start, end):
        self.search_options[constants.PARAM_START_DATE] = start
        self.search_options[constants.PARAM_END_DATE] = end

    def add_collapse(self, periodicity):
        self.periodicity = periodicity

    def add_pagination(self, start, limit, request_start_dates=None):
        self.search_options[constants.PARAM_START] = self.get_es_start(request_start_dates, start)

        offset = start + limit
        extra_offsets = {
            constants.VALUE: 0,
            constants.CHANGE: 1,
            constants.PCT_CHANGE: 1,
            constants.CHANGE_BEG_YEAR: 0,
            constants.PCT_CHANGE_BEG_YEAR: 0,
            constants.CHANGE_YEAR_AGO: extra_offset(self.periodicity),
            constants.PCT_CHANGE_YEAR_AGO: extra_offset(self.periodicity),
        }
        self.search_options[constants.PARAM_START] += extra_offsets[self.rep_mode]
        offset += extra_offsets[self.rep_mode]

        self.search_options[constants.PARAM_LIMIT] = offset

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
        es_start = start - self._serie_first_date_offset(start_date,
                                                         min_date)
        es_start = max(es_start, 0)
        return es_start

    def _serie_first_date_offset(self, series_start_date: datetime, min_start_date: datetime):
        if series_start_date is None or min_start_date is None:
            return 0

        return periods_between(series_start_date, min_start_date, self.periodicity)

    def sort(self, how):
        if how == constants.SORT_ASCENDING:
            sort = settings.TS_TIME_INDEX_FIELD

        elif how == constants.SORT_DESCENDING:
            sort = '-' + settings.TS_TIME_INDEX_FIELD
        else:
            msg = strings.INVALID_SORT_PARAMETER.format(how)
            raise ValueError(msg)

        self.search_options[constants.PARAM_SORT] = sort

    @property
    def search(self):
        if self._search:
            return self._search

        self._search = self._init_search()
        start_date = self.search_options[constants.PARAM_START_DATE]
        end_date = self.search_options[constants.PARAM_END_DATE]
        _filter = {
            'lte': end_date,
            'gte': start_date,
        }
        self._search = self._search.filter('range', timestamp=_filter)

        self._search = self._search.sort(self.search_options[constants.PARAM_SORT])

        self._search = self._search[self.search_options[constants.PARAM_START]:
                                    self.search_options[constants.PARAM_LIMIT]]
        self._add_collapse()
        self._add_collapse_agg()
        return self._search

    def _add_collapse(self):
        if self.collapse_agg not in constants.IN_MEMORY_AGGS:
            self._search = self._search.filter('bool', must=[Q('match', interval=self.periodicity)])

        elif self._has_collapse():
            self._search = self._search.filter('bool', must=[Q('match', interval=self.original_periodicity)])

            interval = self.periodicity
            if interval == 'semester':
                interval = '6M'

            # Agregamos la aggregation (?) para que se ejecute en ES en runtime
            self._search.aggs.bucket('test',
                                     A('date_histogram',
                                       field='timestamp',
                                       interval=interval,
                                       format='yyyy-MM-dd').
                                     metric('test', self.collapse_agg, field=self.rep_mode))
        else:  # Ignoramos la in memory ag
            self.collapse_agg = constants.AGG_DEFAULT
            self._search = self._search.filter('bool', must=[Q('match', interval=self.periodicity)])

    def _add_collapse_agg(self):
        # Si no hay agrupado (collapse), la agregación es sobre un solo valor
        # Sólo tenemos indexado avg en ese caso
        if not self._has_collapse():
            agg = constants.AGG_DEFAULT

        # Si se hace en memoria filtramos por la agg default, y calculamos la agg pedida en runtime
        elif self.collapse_agg in constants.IN_MEMORY_AGGS:
            agg = constants.AGG_DEFAULT

        else:
            agg = self.collapse_agg

        self._search = self._search.filter('bool',
                                           must=[Q('match', aggregation=agg)])

    def _has_collapse(self):
        return self.periodicity != self.original_periodicity
