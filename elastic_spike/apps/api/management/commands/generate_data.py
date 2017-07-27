#! coding: utf-8
import json
import requests
from random import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand

mapping = '''{
  "properties": {
    "timestamp":                    {"type": "date"},
    "value":                        {"type": "scaled_float", "scaling_factor": 10000000},
    "change":                       {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change":               {"type": "scaled_float", "scaling_factor": 10000000},
    "change_a_year_ago":            {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change_a_year_ago":    {"type": "scaled_float", "scaling_factor": 10000000}
  }
}'''


ES_URL = "http://localhost:9200"


class Command(BaseCommand):
    start_date = datetime(2004, 1, 1)
    date_format = '%Y-%m-%dT03:00:00Z'

    def __init__(self):
        self.indicators_count = 0
        self.prev_values = []
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument('--indicators',
                            default=1,
                            type=int,
                            dest='indicators')

        parser.add_argument('--years',
                            default=100,
                            type=int,
                            dest='years')

        parser.add_argument('--interval',
                            default='quarter',
                            type=str,
                            dest='interval',
                            choices=['month', 'quarter', 'year'])

    def handle(self, *args, **options):
        indicators = options['indicators']
        for i in range(indicators):
            self.generate_random_series(options['years'], options['interval'])

    def generate_random_series(self, years, interval):
        self.prev_values.clear()

        # Mapping del indicador
        indic_name = "random-" + str(self.indicators_count)
        url = ES_URL + "/indicators/_mapping/" + indic_name
        requests.put(url, mapping)
        self.stdout.write(indic_name)

        message = ''  # Request de la API de bulk create
        current_date = self.start_date
        end_date = self.start_date + relativedelta(years=years)

        while current_date < end_date:
            date_str = current_date.strftime(self.date_format)

            index_data = {
                "index": {"_id": date_str}
            }
            message += json.dumps(index_data) + '\n'

            properties = self.generate_properties(date_str)
            message += json.dumps(properties) + '\n'

            current_date = self.add_interval(current_date, interval)

        url = ES_URL + "/indicators/" + indic_name + "/_bulk?pretty"
        response = requests.post(url, message)
        # self.stdout.write(response.text)
        self.indicators_count += 1

    @staticmethod
    def add_interval(date, interval):
        months_to_add = 0
        if interval == 'year':
            months_to_add = 12
        elif interval == 'quarter':
            months_to_add = 3
        elif interval == 'month':
            months_to_add = 1
        return date + relativedelta(months=months_to_add)

    def generate_properties(self, date_str):
        """ Genera los valores del indicador aleatoriamente, junto con los
        valores de cambio y porcentuales"""
        properties = {
            'timestamp': date_str,
            'value': 100000 + random() * 10000,
            'change': 1,
            'percent_change': 1,
            'change_a_year_ago': 1,
            'percent_change_a_year_ago': 1
        }

        if len(self.prev_values):
            # Calculos relacionados al valor anterior
            change = self.prev_values[-1]['value'] - properties['value']
            properties['change'] = change
            pct_change = properties['value'] / self.prev_values[-1]['value'] - 1
            properties['percent_change'] = pct_change

            date = datetime.strptime(date_str, self.date_format)
            for prev_value in self.prev_values:
                prev_date = datetime.strptime(prev_value['timestamp'],
                                              self.date_format)

                if date - relativedelta(years=1) == prev_date:
                    # Cálculos relacionados al valor del año pasado
                    change = prev_value['value'] - properties['value']
                    properties['change_a_year_ago'] = change

                    pct_change = properties['value'] / prev_value['value'] - 1
                    properties['percent_change_a_year_ago'] = pct_change
                    break

        self.prev_values.append(properties)
        # Los últimos 12 valores son, en el caso mensual, los del último año.
        # Me quedo sólo con esos valores como optimización
        self.prev_values = self.prev_values[-12:]
        return properties
