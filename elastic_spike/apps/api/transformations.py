#! coding: utf-8

import re
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match


class BaseAggregation:
    date_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self):
        self.result = {'errors': []}
        self.elastic = Elasticsearch()

    def execute(self, series, request_args):
        raise NotImplementedError


class Default(BaseAggregation):
    """Calcula el promedio de una serie en base a el parámetro 'interval'"""

    def execute(self, series, request_args):
        interval = request_args.get('interval', 'year')
        field = request_args.get('field', 'value')
        agg = request_args.get('agg', 'avg')

        self.result['interval'] = interval

        search = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic)

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
            if average.value is None:
                self.result['errors'].append("Valores no encontrados para el intervalo pedido. Pruebe con una granularidad mayor")
                break
            data.append({
                'timestamp': timestamp,
                'value': average.value
            })

        if not self.result['errors']:
            self.result['data'] = data
        return self.result


class Proportion(BaseAggregation):
    """Calcula la proporción de la serie 'series' sobre la original"""

    def execute(self, series, request_args):
        if self.validate_args(request_args):
            other = request_args.get('series', '')
            results = self.execute_search(series, other, request_args)
            if not results:
                return self.result

            # Voy llenando la lista values con los resultados
            values = results[0]
            starting_date = datetime.strptime(results[0][0]['timestamp'],
                                              self.date_format)

            index = 0
            start_date_found = False
            for other_result in results[1]:
                if not start_date_found:
                    new_index = self.find_starting_index(values,
                                                         other_result['timestamp'],
                                                         starting_date)
                    if new_index is None:
                        continue
                    values = values[new_index:]
                    index = 0
                    start_date_found = True

                if index >= len(values):
                    break

                if values[index]['timestamp'] != other_result['timestamp']:
                    self.correct_index(values, index, other_result['timestamp'])

                values[index]['value'] /= other_result['value']
                index += 1
            self.result['data'] = values
            self.result['other_series'] = other

        self.result['series'] = series
        return self.result

    def validate_args(self, request_args):
        other = request_args.get('series', '')

        indices = IndicesClient(client=self.elastic)
        if not other:
            self.result['errors'].append(
                {'error': 'No se pasó un argumento de "series"'}
            )
        elif not indices.exists_type(index="indicators", doc_type=other):
            self.result['errors'].append(
                {'error': 'Serie inválida: {}'.format(other)}
            )
        else:
            return True
        return False

    def execute_search(self, series, other, request_args):
        series_data = Value().execute(series, request_args)
        other_data = Value().execute(other, request_args)
        if series_data['errors'] or other_data['errors']:
            self.result['errors'].extend(series_data['errors'])
            return []
        results = [series_data['data'],
                   other_data['data']]

        self.result['other_series'] = other
        self.result['series'] = series
        self.result['interval'] = series_data['interval']
        return results

    def find_starting_index(self, values, date_str, starting_date):

        date = datetime.strptime(date_str,
                                 self.date_format)
        if date < starting_date:
            return

        for value in values:
            if date_str == value['timestamp']:
                index = values.index(value)
                return index

    def correct_index(self, values, index, current_date_str):
        series_date = datetime.strptime(values[index]['timestamp'],
                                        self.date_format)
        other_date = datetime.strptime(current_date_str,
                                       self.date_format)
        msg = "No se encontró valores de la serie original " \
              "para la fecha: {0} "
        while series_date != other_date:
            self.result['errors'].append(
                msg.format(values[index]['timestamp']))
            values.pop(index)
            series_date = datetime.strptime(
                values[index]['timestamp'],
                self.date_format)


class Value(BaseAggregation):

    def execute(self, series, request_args):

        search = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic).sort('timestamp')

        # No importa si 'to' o 'from' son None
        _from = request_args.get('from')
        _to = request_args.get('to')
        _filter = {
            'lte': _to,
            'gte': _from
        }

        search = search.filter('range', timestamp=_filter)

        rows = request_args.get('rows', 100)
        start = request_args.get('start', 0)
        search = search[start:rows]
        data = []
        for hit in search.execute():
            if hit.value is None:
                self.result['errors'].append("Valores no encontrados para el intervalo pedido. Pruebe con una granularidad mayor")
                break
            data.append({
                'timestamp': hit.timestamp,
                'value': hit.value
            })

        if not self.result['errors']:
            self.result['data'] = data

        self.calc_interval()
        return self.result

    def calc_interval(self):
        # first_date = self.result['data'][0]['timestamp']
        # second_date = self.result['data'][1]['timestamp']
        #
        # first_date = datetime.strptime(first_date, self.date_format)
        # second_date = datetime.strptime(second_date, self.date_format)
        #
        self.result['interval'] = "month"


class Index(BaseAggregation):
    def execute(self, series, request_args):
        base = request_args.get('base')
        field = request_args.get('field', 'value')
        if not base:
            self.result['errors'].append("Base no especificada")
            return self.result

        search = Value().execute(series, request_args)
        search_data = search.get('data')
        if not search_data:
            self.result['errors'].extend(search.get('errors', []))
        else:
            search_base = Search(index="indicators",
                                 doc_type=series,
                                 using=self.elastic).filter()

            search_base.query = Match(timestamp=base)
            result = search_base.execute()
            if not len(result.hits.hits):
                self.result['errors'].append("Base errónea")
                return self.result

            self.result['base'] = result.hits.hits[0]['_id']
            base_value = result.hits.hits[0]['_source'][field]

            for data in search_data:
                data['value'] = data['value'] / base_value * 100
            self.result['data'] = search_data
        return self.result
