#! coding: utf-8
from datetime import datetime
from elasticsearch.client import IndicesClient
from elastic_spike.apps.api.aggregations.base_aggregation import BaseAggregation

from .default import Default


class Proportion(BaseAggregation):
    """Calcula la proporción de la serie 'series' sobre la original"""
    date_format = '%Y-%m-%dT%H:%M:%S.000Z'

    def execute(self, series, request_args, source_data=None):
        if self.validate_args(request_args):
            other = request_args.get('series', '')
            results = self.execute_search(series, other, request_args)
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
        request_args['agg'] = 'avg'
        series_data = Default().execute(series, request_args)
        results = [series_data['data'],
                   Default().execute(other, request_args)['data']]

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
