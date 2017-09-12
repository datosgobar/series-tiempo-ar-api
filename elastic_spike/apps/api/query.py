#! coding: utf-8
import re
from abc import abstractmethod
from datetime import datetime

from django.conf import settings
from elasticsearch.client import IndicesClient, Elasticsearch
from elasticsearch_dsl import Search, MultiSearch


class QueryPipeline:
    def __init__(self, query_args):
        self.args = query_args
        self.result = {}
        self.elastic = Elasticsearch()
        self.commands = self.init_commands()
        self.run()

    def run(self):
        query = Query()
        for cmd in self.commands:
            cmd_instance = cmd()
            cmd_instance.run(query, self.args)
            if cmd_instance.errors:
                self.result['errors'] = cmd_instance.errors.copy()
                return

        self.result['data'] = query.data

    @staticmethod
    def init_commands():
        """Lista con las operaciones a ejecutar"""
        return [
            NameAndRepMode,
            DateFilter,
            Pagination,
            Execute
        ]


class Query:
    """Representa una query de la API de series de tiempo, que termina
    devolviendo resultados de datos leídos de ElasticSearch"""
    def __init__(self):
        """
        Instancia una nueva query

        args:
            series (str):  Nombre de una serie
            parameters (dict): Opciones de la query
        """
        self.series = []
        self.elastic = Elasticsearch()
        self.result = {}
        self.data = []

    def add_pagination(self, start, limit):
        if not len(self.series):
            self.series.append({'search': Search(using=self.elastic)})

        for serie in self.series:
            serie['search'] = serie['search'][start:limit]

    def add_filter(self, start, end):
        if not len(self.series):
            self.series.append({'search': Search(using=self.elastic)})

        _filter = {
            'lte': end,
            'gte': start
        }
        for serie in self.series:
            serie['search'] = serie['search'].filter('range',
                                                     timestamp=_filter)

    def add_series(self, series_id, rep_mode):
        if len(self.series) == 1:
            search = self.series[0]['search'].doc_type(id)
        else:
            search = Search(doc_type=series_id)

        self.series.append({
            'search': search,
            'rep_mode': rep_mode
        })

    def run(self):
        multi_search = MultiSearch(index=settings.TS_INDEX,
                                   using=self.elastic)

        for serie in self.series:
            multi_search = multi_search.add(serie['search'])

        responses = multi_search.execute()
        self.format_response(responses)

    def format_response(self, responses):
        for i, response in enumerate(responses):
            rep_mode = self.series[i]['rep_mode']
            self.populate_data(response, rep_mode)

    def populate_data(self, response, rep_mode):
        for i, hit in enumerate(response):
            if i == len(self.data):
                data_row = [hit.timestamp]
                self.data.append(data_row)
            self.data[i].append(hit[rep_mode])


class BaseOperation:
    def __init__(self):
        self.errors = []

    @abstractmethod
    def run(self, query, args):
        """Ejecuta la operación del pipeline sobre el parámetro series
        
        Args:
            query (dict): diccionario que represente a una serie, con
            por lo menos 'search' (de tipo elasticsearch-dsl.Search)
            args: parámetros del comando a ejecutar
        Returns:
            dict: nuevo objeto series, modificado
        """
        raise NotImplementedError

    def append_error(self, msg):
        self.errors.append({
            'error': msg
        })


class Pagination(BaseOperation):
    """Agrega paginación de resultados a una búsqueda"""
    def run(self, query, args):
        start = args.get('start', settings.API_DEFAULT_VALUES['start'])
        limit = args.get('limit', settings.API_DEFAULT_VALUES['limit'])
        self.validate_arg(start)
        self.validate_arg(limit, min_value=1)
        if self.errors:
            raise ValueError

        start = int(start)
        limit = start + int(limit)
        query.add_pagination(start, limit)

    def validate_arg(self, arg, min_value=0):
        try:
            parsed_arg = int(arg)
        except ValueError:
            parsed_arg = None

        if parsed_arg is None or parsed_arg < min_value:
            self.append_error("Parámetro 'limit' inválido: {}".format(arg))


class DateFilter(BaseOperation):
    def __init__(self):
        super().__init__()
        self.start = None
        self.end = None

    def run(self, query, args):
        self.start = args.get('start_date')
        self.end = args.get('end_date')

        self.validate_start_end_dates()
        if self.errors:
            raise ValueError

        query.add_filter(self.start, self.end)

    def validate_start_end_dates(self):
        """Valida el intervalo de fechas (start, end). Actualiza la
        lista de errores de ser necesario.
        """

        parsed_start, parsed_end = None, None
        if self.start:
            try:
                parsed_start = self.validate_date(self.start)
            except ValueError:
                pass

        if self.end:
            try:
                parsed_end = self.validate_date(self.end)
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


class NameAndRepMode(BaseOperation):
    """Asigna el doc_type a la búsqueda, el identificador de cada
    serie de tiempo individual, y rep_mode, el modo de representación
    """
    def __init__(self):
        super().__init__()
        self.elastic = Elasticsearch()
        self.ids = None

    def run(self, query, args):
        self.ids = args.get('ids')
        if not self.ids:
            self.append_error('No se especificó una serie de tiempo.')
            return

        name, rep_mode = self.parse_series(self.ids, args)
        self.validate(name, rep_mode)

        query.add_series(name, rep_mode)

    def validate(self, doc_type, rep_mode):
        indices = IndicesClient(client=self.elastic)
        if not indices.exists_type(index="indicators",
                                   doc_type=doc_type):
            self.append_error('Serie inválida: {}'.format(self.ids))

        if rep_mode not in settings.REP_MODES:
            error = "Modo de representación inválido: {}".format(rep_mode)
            self.append_error(error)

    def parse_series(self, serie, args):
        """Parsea una serie invididual. Actualiza la lista de errores
            en caso de encontrar alguno
        Args:
            serie (str): string con formato de tipo 'id:rep_mode'
            args (dict): argumentos de la query
        
        Returns:
            nombre y rep_mode parseados
        """

        # rep_mode 'default', para todas las series, overrideado
        # si la serie individual especifica alguno
        rep_mode = args.get('representation-mode',
                            settings.API_DEFAULT_VALUES['rep_mode'])
        colon_index = serie.find(':')
        if colon_index < 0:
            name = serie
        else:
            try:
                name, rep_mode = serie.split(':')
            except ValueError:
                self.append_error("Formato de series a seleccionar inválido")
                return
        return name, rep_mode


class Execute(BaseOperation):

    def run(self, query, args):
        query.run()
