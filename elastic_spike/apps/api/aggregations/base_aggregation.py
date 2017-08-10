#! coding: utf-8

import re
from datetime import datetime
from elasticsearch import Elasticsearch


class BaseAggregation:
    date_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self):
        self.result = {'errors': []}
        self.elastic = Elasticsearch()

    def execute(self, series, request_args):
        raise NotImplementedError

    def interval_filter(self, _from, _to, search):
        if _from or _to:
            valid = self.validate_from_to_dates(_from, _to)
            if not valid:
                raise ValueError
        _filter = {
            'lte': _to,
            'gte': _from
        }

        return search.filter('range', timestamp=_filter)

    def validate_from_to_dates(self, _from, _to):
        """Devuelve un booleano que indica si el intervalo (_to, _from) es
        válido. Actualiza la lista de errores de ser necesario"""
        parsed_from, parsed_to = None, None
        if _from:
            try:
                parsed_from = self.parse_interval_date(_from)
            except ValueError:
                return False

        if _to:
            try:
                parsed_to = self.parse_interval_date(_to)
            except ValueError:
                return False

        if parsed_from and parsed_to:
            if parsed_from > parsed_to:
                self.result['errors'].append("Filtro por rango temporal inválido (from > to)")
                return False
        return True

    def parse_interval_date(self, interval):
        full_date = r'\d{4}-\d{2}-\d{2}'
        year_and_month = r'\d{4}-\d{2}'
        year_only = r'\d{4}'

        if re.fullmatch(full_date, interval):
            result = datetime.strptime(interval, '%Y-%m-%d')
        elif re.fullmatch(year_and_month, interval):
            result = datetime.strptime(interval, "%Y-%m")
        elif re.fullmatch(year_only, interval):
            result = datetime.strptime(interval, "%Y")
        else:
            self.result['errors'].append('Formato de rango temporal inválido')
            raise ValueError
        return result
