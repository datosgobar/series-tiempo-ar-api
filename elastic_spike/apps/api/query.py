#! coding: utf-8
import re
from datetime import datetime

from django.conf import settings
from elasticsearch.client import IndicesClient, Elasticsearch

from elastic_spike.apps.api.transformations import Value


class Query:
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""
    def __init__(self, query_args):
        """
        Instancia una nueva query
        
        args:
            series (str):  Nombre de una serie
            parameters (dict): Opciones de la query
        """
        self.series = []
        self.args = query_args
        self.elastic = Elasticsearch()
        self.result = {}
        if not self.validate_args():
            return

        self.run()

    def run(self):
        search = Value(self.series, self.args)
        pass

        result = {
            'data': search.data,
            'errors': search.errors,
            'length': len(search.data)
        }
        self.result.update(result)

    def validate_args(self):
        """Valida los parámetros recibidos. Si encuentra errores va
        agregandolos a los resultados. Los argumentos serán válidos
        si luego de todas las validaciones no se encontró ningún
        error. En ese caso devuelve True, de haber errores, False
        """

        series = self.args.get('series')
        if not series:
            self.append_error('No se especificó una serie de tiempo')
        else:
            for serie in series.split(','):
                self.split_single_series(serie)

        self.validate_from_to_dates()
        self.validate_pagination('limit')
        self.validate_pagination('start')

        return len(self.result['errors']) == 0

    def validate_pagination(self, arg):
        """Valida la conversión de parámetros que deberían
        interpretarse como valores numéricos
        """
        arg = self.args.get(arg)
        if not arg:
            return

        try:
            parsed_arg = int(arg)
        except ValueError:
            parsed_arg = None

        if parsed_arg is None or parsed_arg < 0:
            self.append_error("Parámetro 'limit' inválido: {}".format(arg))
        elif arg == 'limit' and parsed_arg < 1:
            self.append_error("Parámetro 'limit' inválido: {}".format(arg))

    def split_single_series(self, serie):
        rep_mode = settings.API_DEFAULT_VALUES['rep_mode']
        colon_index = serie.find(':')
        if colon_index < 0:
            name = serie
        else:
            name, rep_mode = serie.split(':')
            if rep_mode not in settings.REP_MODES:
                error = "Modo de representación inválido: {}".format(rep_mode)
                self.append_error(error)
                return False

        self.series.append({
            'name': name,
            'rep_mode': rep_mode
        })

        indices = IndicesClient(client=self.elastic)
        if not indices.exists_type(index="indicators", doc_type=name):
            self.append_error('Serie inválida: {}'.format(name))
            return False
        return True

    def append_error(self, msg):
        if self.result.get('errors') is None:
            self.result['errors'] = []

        self.result['errors'].append({
            'error': msg
        })

    def validate_from_to_dates(self):
        """Devuelve un booleano que indica si el intervalo
        (_to, _from) es válido. Actualiza la lista de errores de ser
        necesario.
        """
        _from = self.args.get('from')
        _to = self.args.get('to')
        parsed_from, parsed_to = None, None
        if _from:
            try:
                parsed_from = self.parse_interval_date(_from)
            except ValueError:
                pass

        if _to:
            try:
                parsed_to = self.parse_interval_date(_to)
            except ValueError:
                pass

        if parsed_from and parsed_to:
            if parsed_from > parsed_to:
                error = "Filtro por rango temporal inválido (from > to)"
                self.append_error(error)
                return False
        return True

    def parse_interval_date(self, interval):
        full_date = r'\d{4}-\d{2}-\d{2}'
        year_and_month = r'\d{4}-\d{2}'
        year_only = r'\d{4}'

        if re.fullmatch(full_date, interval):
            parsed_date = datetime.strptime(interval, '%Y-%m-%d')
        elif re.fullmatch(year_and_month, interval):
            parsed_date = datetime.strptime(interval, "%Y-%m")
        elif re.fullmatch(year_only, interval):
            parsed_date = datetime.strptime(interval, "%Y")
        else:
            error = 'Formato de rango temporal inválido: {}'.format(interval)
            self.append_error(error)
            raise ValueError
        return parsed_date
