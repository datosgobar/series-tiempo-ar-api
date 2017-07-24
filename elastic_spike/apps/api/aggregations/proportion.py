#! coding: utf-8
from datetime import datetime
from elasticsearch.client import IndicesClient
from elasticsearch_dsl import Search, MultiSearch
from elastic_spike.apps.api.aggregations.BaseAggregation import BaseAggregation


class Proportion(BaseAggregation):
    """Calcula la proporción de la serie 'series' sobre la original"""
    name = "proporción"
    date_format = '%Y-%m-%dT%H:%M:%SZ'

    def execute(self, series, request_args):
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
            s1 = Search(index="indicators",
                        doc_type=series,
                        using=self.elastic).source(fields=['value']).sort('timestamp')[:10000]
            s2 = Search(index="indicators",
                        doc_type=other,
                        using=self.elastic).source(fields=['value']).sort('timestamp')[:10000]

            ms = MultiSearch(index="indicators",
                             using=self.elastic).add(s1).add(s2)

            results = ms.execute()
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
                    date = datetime.strptime(other_result.meta.id,
                                             self.date_format)
                    if date < starting_date:
                        continue
                    elif date > starting_date:
                        for value in values:
                            if other_result.meta.id == value['timestamp']:
                                index = values.index(value)
                                break
                        values = values[index:]
                        index = 0
                        start_date_found = True

                if index >= len(values):
                    break

                if values[index]['timestamp'] != other_result.meta.id:
                    series_date = datetime.strptime(values[index]['timestamp'],
                                                    self.date_format)
                    other_date = datetime.strptime(other_result.meta.id,
                                                   self.date_format)
                    msg = "No se encontró valores de la serie original " \
                          "para la fecha: {0} "
                    while series_date != other_date:
                        self.result['errors'].append(
                            msg.format(values[index]['timestamp']))
                        values.pop(index)
                        series_date = datetime.strptime(values[index]['timestamp'],
                                                        self.date_format)

                values[index]['value'] /= other_result.value
                index += 1
            self.result['data'] = values
        return self.result

