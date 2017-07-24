#! coding: utf-8
from datetime import datetime
from elasticsearch.client import IndicesClient
from elasticsearch_dsl import Search, MultiSearch
from elastic_spike.apps.api.aggregations.base_aggregation import BaseAggregation


class Proportion(BaseAggregation):
    """Calcula la proporción de la serie 'series' sobre la original"""
    name = "proporción"
    date_format = '%Y-%m-%dT%H:%M:%SZ'

    def execute(self, series, request_args, source_data=None):
        if self.validate_args(request_args):
            other = request_args.get('series', '')
            results = self.execute_search(series, other)
            # Voy llenando la lista values con los resultados
            values = []
            starting_date = datetime.strptime(results[0][0].meta.id,
                                              self.date_format)
            # Primero lleno con los datos de la serie original
            for series_result in results[0]:
                values.append({
                    'value': series_result.value,
                    'timestamp': series_result.meta.id
                })

            index = 0
            start_date_found = False
            for other_result in results[1]:
                if not start_date_found:
                    new_index = self.find_starting_index(values,
                                                         other_result.meta.id,
                                                         starting_date)
                    if not new_index:
                        continue
                    values = values[new_index:]
                    index = 0
                    start_date_found = True

                if index >= len(values):
                    break

                if values[index]['timestamp'] != other_result.meta.id:
                    self.correct_index(values, index, other_result.meta.id)

                values[index]['value'] /= other_result.value
                index += 1
            self.result['data'] = values
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

    def execute_search(self, series, other):
        series_search = Search(index="indicators",
                               doc_type=series,
                               using=self.elastic) \
            .source(fields=['value']) \
            .sort('timestamp')[:10000]

        other_search = Search(index="indicators",
                              doc_type=other,
                              using=self.elastic) \
            .source(fields=['value']) \
            .sort('timestamp')[:10000]

        search = MultiSearch(index="indicators", using=self.elastic) \
            .add(series_search) \
            .add(other_search)

        results = search.execute()
        return results

    def find_starting_index(self, values, date_str, starting_date):

        date = datetime.strptime(date_str,
                                 self.date_format)
        if date < starting_date:
            return False
        elif date > starting_date:
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
