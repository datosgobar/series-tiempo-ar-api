#! coding: utf-8
import re
from datetime import datetime

from django.conf import settings
from elasticsearch.client import IndicesClient, Elasticsearch

from elastic_spike.apps.api.transformations import Value, Collapse


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
        if 'collapse' in self.args:
            search = Collapse(self.series, self.args)
        else:
            search = Value(self.series, self.args)

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

        self.validate_pagination('limit')
        self.validate_pagination('start')
        self.validate_start_end_dates()

        series = self.args.get('series')
        if not series:
            self.append_error('No se especificó una serie de tiempo')
        else:
            for serie in series.split(','):
                self.split_single_series(serie)

        return self.result.get('errors') is None

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

    def validate_start_end_dates(self):
        """Devuelve un booleano que indica si el intervalo
        (end, start) es válido. Actualiza la lista de errores de ser
        necesario.
        """
        start = self.args.get('start_date')
        end = self.args.get('end_date')
        parsed_start, parsed_end = None, None
        if start:
            try:
                parsed_start = self.validate_date(start)
            except ValueError:
                pass

        if end:
            try:
                parsed_end = self.validate_date(end)
            except ValueError:
                pass

        if parsed_start and parsed_end:
            if parsed_start > parsed_end:
                error = "Filtro por rango temporal inválido (start > end)"
                self.append_error(error)

    def validate_date(self, date):
        full_date = r'\d{4}-\d{2}-\d{2}'
        year_and_month = r'\d{4}-\d{2}'
        year_only = r'\d{4}'

        if re.fullmatch(full_date, date):
            parsed_date = datetime.strptime(date, '%Y-%m-%d')
        elif re.fullmatch(year_and_month, date):
            parsed_date = datetime.strptime(date, "%Y-%m")
        elif re.fullmatch(year_only, date):
            parsed_date = datetime.strptime(date, "%Y")
        else:
            error = 'Formato de rango temporal inválido: {}'.format(date)
            self.append_error(error)
            raise ValueError
        return parsed_date

    def validate_rep_mode(self):
        rep_mode = self.args.get('representation-mode')
        if rep_mode not in settings.REP_MODES:
            error = "Modo de representación global inválido: {}".format(rep_mode)
            self.append_error(error)

    def split_single_series(self, serie):
        if not serie:
            self.append_error("Formato de series a seleccionar inválido")
            return

        # rep_mode 'default', para todas las series, overrideado
        # si la serie individual especifica alguno
        rep_mode = self.args.get('representation-mode')
        if rep_mode is None:
            rep_mode = settings.API_DEFAULT_VALUES['rep_mode']

        colon_index = serie.find(':')
        if colon_index < 0:
            name = serie
        else:
            try:
                name, rep_mode = serie.split(':')
            except ValueError:
                self.append_error("Formato de series a seleccionar inválido")
                return

            if rep_mode not in settings.REP_MODES:
                error = "Modo de representación inválido: {}".format(rep_mode)
                self.append_error(error)

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
