#! coding: utf-8

from datetime import datetime
import re
from elasticsearch_dsl import Search
from elastic_spike.apps.api.aggregations.base_aggregation import BaseAggregation


class Default(BaseAggregation):
    """Calcula el promedio de una serie en base a el parámetro 'interval'"""

    date_format = '%Y-%m-%d'
    def execute(self, series, request_args):
        interval = request_args.get('interval', 'year')
        field = request_args.get('field', 'value')
        agg = request_args.get('agg', 'avg')

        self.result['interval'] = interval

        _from = request_args.get('from')
        _to = request_args.get('to')
        if _from or _to:
            valid = self.validate_from_to_dates(_from, _to)
            if not valid:
                return self.result

        _filter = {
            'lte': _to,
            'gte': _from
        }
        search = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic)
        search = search.filter('range', timestamp=_filter)

        # Le decimos a Elastic que no devuelva resultados, nos interesa solo
        # el aggregation
        search = search[:0]

        search.aggs.bucket('agg',
                           'date_histogram',
                           field='timestamp',
                           interval=interval).metric('agg',
                                                     agg,
                                                     field=field)

        search_result = search.execute()
        data = []
        for element in search_result.aggregations.agg.buckets:
            timestamp = element['key_as_string']
            average = element['agg']
            if not average.value:
                self.result['errors'].append("Valores no encontrados para el intervalo pedido. Pruebe con una granularidad mayor")
                break
            data.append({
                'timestamp': timestamp,
                'value': average.value
            })

        if not self.result['errors']:
            self.result['data'] = data
        return self.result

    def validate_from_to_dates(self, _from, _to):
        """Devuelve un booleano que indica si el intervalo (_to, _from) es
        válido. Actualiza la lista de errores de ser necesario"""
        parsed_from, parsed_to = None, None
        if _from:
            parsed_from = self.parse_interval_date(_from)
            if not parsed_from:
                return False

        if _to:
            parsed_to = self.parse_interval_date(_to)
            if not parsed_to:
                return False

        if parsed_from and parsed_to:
            if parsed_from > parsed_to:
                self.result['errors'].append("Filtro por rango temporal inválido (from > to)")
                return False
        return True

    def parse_interval_date(self, interval):
        full_date = '\d{4}-\d{2}-\d{2}'
        year_and_month = '\d{4}-\d{2}'
        year_only = '\d{4}'

        result = False
        if re.fullmatch(full_date, interval):
            result = datetime.strptime(interval, '%Y-%m-%d')
        elif re.fullmatch(year_and_month, interval):
            result = datetime.strptime(interval, "%Y-%m")
        elif re.fullmatch(year_only, interval):
            result = datetime.strptime(interval, "%Y")
        else:
            self.result['errors'].append('Formato de rango temporal inválido')
        return result

