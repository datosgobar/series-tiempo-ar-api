#! coding: utf-8
import re

from datetime import datetime
from elasticsearch.client import IndicesClient, Elasticsearch

from elastic_spike.apps.api.transformations import Value


class Query:
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""
    def __init__(self, series, query_args):
        """
        Instancia una nueva query
        
        args:
            series (str):  Nombre de una serie
            parameters (dict): Opciones de la query
        """
        self.series = series
        self.args = query_args
        self.elastic = Elasticsearch()
        self.result = {
            'errors': []
        }
        if not self.validate_args():
            return

        self.run()

    def run(self):
        self.result.update(Value().execute(self.series, self.args))
        return self.result

    def validate_args(self):
        """Valida los parámetros recibidos"""
        if not self.series:
            self.append_error('No se especificó una serie de tiempo')
            return False

        indices = IndicesClient(client=self.elastic)
        if not indices.exists_type(index="indicators", doc_type=self.series):
            self.append_error('Serie inválida: {}'.format(self.series))
            return False

        _from = self.args.get('from')
        _to = self.args.get('to')
        if not self.validate_from_to_dates(_from, _to):
            return False

        return True

    def append_error(self, msg):
        self.result['errors'].append({
            'error': msg
        })

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
                self.append_error("Filtro por rango temporal inválido (from > to)")
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
            self.append_error('Formato de rango temporal inválido')
            raise ValueError
        return result
