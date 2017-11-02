#! coding: utf-8
from abc import abstractmethod
from calendar import monthrange
from datetime import date

import iso8601
from django.conf import settings

from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.api.query.query import Query
from .query.exceptions import CollapseError


class QueryPipeline(object):
    """Pipeline del proceso de queries de la serie de tiempo. Ejecuta
    varias operaciones o comandos sobre un objeto query, usando los
    parámetros pasados por el request"""
    def __init__(self, request_args):
        """
        Args:
            request_args (dict): dict con los parámetros del GET
                request
        """
        self.args = request_args
        self.commands = self.init_commands()

    def run(self):
        query = Query()
        response = {}
        for cmd in self.commands:
            cmd_instance = cmd()
            query = cmd_instance.run(query, self.args)
            if cmd_instance.errors:
                response['errors'] = list(cmd_instance.errors)
                return response

        response = self.generate_response(query)
        return response

    def generate_response(self, query):
        response = {}

        if query.data:  # Puede ser vacío en el caso de sólo metadatos
            response['data'] = query.data

        if query.get_metadata():  # Puede ser vacío en el caso de sólo datos
            response['meta'] = query.get_metadata()

        return response

    @staticmethod
    def init_commands():
        """Lista con las operaciones a ejecutar. La lista de comandos
        tiene un orden arbitrario y no debería importar, excepto el
        comando que ejecute la búsqueda, que debería estar al final
        """
        return [
            NameAndRepMode,
            DateFilter,
            Pagination,
            Collapse,
            Execute,
            Metadata
        ]


class BaseOperation(object):
    def __init__(self):
        self.errors = []

    @abstractmethod
    def run(self, query, args):
        """Ejecuta la operación del pipeline sobre el parámetro query

        Args:
            query (ESQuery)
            args (dict): parámetros del request
        Returns:
            ESQuery: nuevo objeto query, el original con la operación
                pertinente aplicada
        """
        raise NotImplementedError

    def _append_error(self, msg):
        self.errors.append({
            'error': msg
        })


class Pagination(BaseOperation):
    """Agrega paginación de resultados a una búsqueda"""

    def run(self, query, args):
        start = args.get('start', settings.API_DEFAULT_VALUES['start'])
        limit = args.get('limit', settings.API_DEFAULT_VALUES['limit'])
        self.validate_arg(start, name='start')
        self.validate_arg(limit, min_value=1, name='limit')
        if self.errors:
            return query

        start = int(start)
        limit = start + int(limit)
        query.add_pagination(start, limit)
        return query

    def validate_arg(self, arg, min_value=0, name='limit'):
        try:
            parsed_arg = int(arg)
        except ValueError:
            parsed_arg = None

        if parsed_arg is None or parsed_arg < min_value:
            self._append_error("Parámetro '{}' inválido: {}".format(name, arg))
            return

        max_value = settings.MAX_ALLOWED_VALUE[name]
        if parsed_arg > max_value:
            msg = "Parámetro {} por encima del límite permitido ({})"
            self._append_error(msg.format(name, max_value))


class DateFilter(BaseOperation):
    def __init__(self):
        BaseOperation.__init__(self)
        self.start = None
        self.end = None

    def run(self, query, args):
        self.start = args.get('start_date')
        self.end = args.get('end_date')

        self.validate_start_end_dates()
        if self.errors:
            return query

        start_date, end_date = None, None
        if self.start:
            start_date = str(iso8601.parse_date(self.start).date())
        if self.end:
            end_date = iso8601.parse_date(self.end).date()
            if '-' not in self.end:  # Solo especifica año
                end_date = date(end_date.year, 12, 31)
            if self.end.count('-') == 1:  # Especifica año y mes
                # Obtengo el último día del mes, monthrange devuelve
                # tupla (month, last_day)
                days = monthrange(end_date.year, end_date.month)[1]
                end_date = date(end_date.year, end_date.month, days)

        query.add_filter(start_date, end_date)
        return query

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
                self._append_error(error)

    def validate_date(self, date):
        """Valida y parsea la fecha pasada.

        Args:
            date (str): date string, ISO 8601

        Returns:
            date con la fecha parseada

        Raises:
            ValueError: si el formato no es válido
        """

        try:
            parsed_date = iso8601.parse_date(date)
        except iso8601.ParseError:
            error = 'Formato de rango temporal inválido: {}'.format(date)
            self._append_error(error)
            raise ValueError
        return parsed_date


class NameAndRepMode(BaseOperation):
    """Asigna el doc_type a la búsqueda, el identificador de cada
    serie de tiempo individual, y rep_mode, el modo de representación,
    a base de el parseo el parámetro 'ids', que contiene datos de
    varias series a la vez
    """

    def __init__(self):
        BaseOperation.__init__(self)
        self.ids = None

    def run(self, query, args):
        self.ids = args.get('ids')
        if not self.ids:
            self._append_error('No se especificó una serie de tiempo.')
            return

        name, rep_mode = self._parse_series(self.ids, args)
        self._validate(name, rep_mode)

        query.add_series(name, rep_mode)
        return query

    def _validate(self, doc_type, rep_mode):
        """Valida si el 'doc_type' es válido, es decir, si la serie
        pedida es un ID contenido en la base de datos. De no
        encontrarse, llena la lista de errores según corresponda.
        """
        if not Field.objects.filter(series_id=doc_type):
            self._append_error('Serie inválida: {}'.format(self.ids))

        if rep_mode not in settings.REP_MODES:
            error = "Modo de representación inválido: {}".format(rep_mode)
            self._append_error(error)

    def _parse_series(self, serie, args):
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
        rep_mode = args.get('representation_mode',
                            settings.API_DEFAULT_VALUES['rep_mode'])
        colon_index = serie.find(':')
        if colon_index < 0:
            name = serie
        else:
            try:
                name, rep_mode = serie.split(':')
            except ValueError:
                self._append_error("Formato de series a seleccionar inválido")
                return
        return name, rep_mode


class Collapse(BaseOperation):
    """Maneja las distintas agregaciones (suma, promedio)"""
    def run(self, query, args):
        collapse = args.get('collapse')
        if not collapse:
            return query

        if collapse not in settings.COLLAPSE_INTERVALS:
            msg = 'Intervalo de agregación inválido: {}'
            self._append_error(msg.format(collapse))
            return query

        agg = args.get('collapse_aggregation',
                       settings.API_DEFAULT_VALUES['collapse_aggregation'])
        rep_mode = args.get('representation_mode',
                            settings.API_DEFAULT_VALUES['rep_mode'])

        if agg not in settings.AGGREGATIONS:
            self._append_error("Modo de agregación inválido: {}".format(agg))
        else:
            try:
                query.add_collapse(agg, collapse, rep_mode)
            except CollapseError:
                msg = "Intervalo de collapse inválido para la(s) serie(s) " \
                      "seleccionadas: {}. Pruebe con un intervalo mayor"
                msg = msg.format(collapse)
                self._append_error(msg)
        return query


class Metadata(BaseOperation):

    def run(self, query, args):
        metadata = args.get('metadata')
        if not metadata:
            return query

        if metadata not in settings.METADATA_SETTINGS:
            msg = u'Configuración de metadatos inválido: {}'.format(metadata)
            self._append_error(msg)
        else:
            query.set_metadata_config(metadata)

        return query


class Execute(BaseOperation):
    def run(self, query, args):
        query.run()
        return query
