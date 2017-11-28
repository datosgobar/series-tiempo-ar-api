#! coding: utf-8
import datetime
from abc import abstractmethod
from calendar import monthrange

import iso8601
from django.conf import settings
from django.http import JsonResponse
from elasticsearch import TransportError

from series_tiempo_ar_api.apps.api.exceptions import CollapseError
from series_tiempo_ar_api.apps.api.models import Field
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.query.response import \
    ResponseFormatterGenerator
from series_tiempo_ar_api.apps.api.query.strings import SERIES_DOES_NOT_EXIST
from series_tiempo_ar_api.apps.api.query import strings
from series_tiempo_ar_api.apps.api.query import constants


class QueryPipeline(object):
    """Pipeline del proceso de queries de la serie de tiempo. Ejecuta
    varias operaciones o comandos sobre un objeto query, usando los
    parámetros pasados por el request"""
    def __init__(self):
        self.commands = self.init_commands()

    def run(self, args):
        query = Query()
        for cmd in self.commands:
            cmd_instance = cmd()
            cmd_instance.run(query, args)
            if cmd_instance.errors:
                return self.generate_error_response(cmd_instance.errors)

        _format = args.get(constants.PARAM_FORMAT,
                           constants.API_DEFAULT_VALUES[constants.PARAM_FORMAT])
        formatter = self.get_formatter(_format)
        try:
            return formatter.run(query, args)
        except TransportError:
            return self.generate_error_response([strings.ELASTICSEARCH_ERROR])

    @staticmethod
    def generate_error_response(errors_list):
        response = {'errors': list(errors_list)}
        return JsonResponse(response, status=constants.RESPONSE_ERROR_CODE)

    @staticmethod
    def get_formatter(_format):
        generator = ResponseFormatterGenerator(_format)
        return generator.get_formatter()

    @staticmethod
    def init_commands():
        """Lista con las operaciones a ejecutar. La lista de comandos
        tiene un orden arbitrario y no debería importar, excepto el
        comando que ejecute la búsqueda, que debería estar al final
        """
        return [
            IdsField,
            DateFilter,
            Pagination,
            Sort,
            Collapse,
            Metadata,
            Format
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
        start = args.get(constants.PARAM_START,
                         constants.API_DEFAULT_VALUES[constants.PARAM_START])
        limit = args.get(constants.PARAM_LIMIT,
                         constants.API_DEFAULT_VALUES[constants.PARAM_LIMIT])
        self.validate_arg(start, name=constants.PARAM_START)
        self.validate_arg(limit, min_value=1, name=constants.PARAM_LIMIT)
        if self.errors:
            return

        start = int(start)
        limit = start + int(limit)
        query.add_pagination(start, limit)

    def validate_arg(self, arg, min_value=0, name=constants.PARAM_LIMIT):
        try:
            parsed_arg = int(arg)
        except ValueError:
            parsed_arg = None

        if parsed_arg is None or parsed_arg < min_value:
            self._append_error(strings.INVALID_PARAMETER.format(name, arg))
            return

        max_value = settings.MAX_ALLOWED_VALUES[name]
        if parsed_arg > max_value:
            msg = strings.PARAMETER_OVER_LIMIT.format(name, max_value, parsed_arg)
            self._append_error(msg)


class DateFilter(BaseOperation):
    def __init__(self):
        BaseOperation.__init__(self)
        self.start = None
        self.end = None

    def run(self, query, args):
        self.start = args.get(constants.PARAM_START_DATE)
        self.end = args.get(constants.PARAM_END_DATE)

        self.validate_start_end_dates()
        if self.errors:
            return

        start_date, end_date = None, None
        if self.start:
            start_date = str(iso8601.parse_date(self.start).date())
        if self.end:
            end_date = iso8601.parse_date(self.end).date()
            if '-' not in self.end:  # Solo especifica año
                end_date = datetime.date(end_date.year, 12, 31)
            if self.end.count('-') == 1:  # Especifica año y mes
                # Obtengo el último día del mes, monthrange devuelve
                # tupla (month, last_day)
                days = monthrange(end_date.year, end_date.month)[1]
                end_date = datetime.date(end_date.year, end_date.month, days)

        query.add_filter(start_date, end_date)

    def validate_start_end_dates(self):
        """Valida el intervalo de fechas (start, end). Actualiza la
        lista de errores de ser necesario.
        """

        parsed_start, parsed_end = None, None
        if self.start:
            try:
                parsed_start = self.validate_date(self.start,
                                                  constants.PARAM_START_DATE)
            except ValueError:
                pass

        if self.end:
            try:
                parsed_end = self.validate_date(self.end,
                                                constants.PARAM_END_DATE)
            except ValueError:
                pass

        if parsed_start and parsed_end:
            if parsed_start > parsed_end:
                self._append_error(strings.INVALID_DATE_FILTER)

    def validate_date(self, _date, param):
        """Valida y parsea la fecha pasada.

        Args:
            _date (str): date string, ISO 8601
            param (str): Parámetro siendo parseado

        Returns:
            date con la fecha parseada

        Raises:
            ValueError: si el formato no es válido
        """

        try:
            parsed_date = iso8601.parse_date(_date)
        except iso8601.ParseError:
            self._append_error(strings.INVALID_DATE.format(param, _date))
            raise ValueError
        return parsed_date


class IdsField(BaseOperation):
    """Asigna las series_ids, con sus modos de representación y modos de agregación,
    a base de el parseo el parámetro 'ids', que contiene datos de varias series a la vez
    """

    def __init__(self):
        BaseOperation.__init__(self)
        # Lista EN ORDEN de las operaciones de collapse a aplicar a las series
        self.aggs = []

    def run(self, query, args):
        # Ejemplo de formato del parámetro 'ids':
        # serie1:rep_mode1:agg1,serie2:repmode2:agg2,serie3:agg3,serie4:rep_mode3
        # rep_mode y agg son opcionales, hay un valor default, dado por otros parámetros
        # 'representation_mode' y 'collapse_aggregation'
        # Parseamos esa string y agregamos a la query las series pedidas
        ids = args.get(constants.PARAM_IDS)
        rep_mode = args.get(constants.PARAM_REP_MODE,
                            constants.API_DEFAULT_VALUES[constants.PARAM_REP_MODE])
        if not ids:
            self._append_error(strings.NO_TIME_SERIES_ERROR)
            return

        delim = ids.find(',')
        series = ids.split(',') if delim > -1 else [ids]
        for serie_string in series:
            self.process_serie_string(query, serie_string, rep_mode)

    def process_serie_string(self, query, serie_string, default_rep_mode):
        name, rep_mode, collapse_agg = self._parse_single_series(serie_string)

        if not rep_mode:
            rep_mode = default_rep_mode

        if self.errors:
            error = strings.INVALID_SERIES_IDS_FORMAT
            self._append_error(error)
            return

        self.add_series(query, name, rep_mode, collapse_agg)

        if self.errors:
            return

    def add_series(self, query, series_id, rep_mode, collapse_agg):
        field_model = self._get_model(series_id, rep_mode)
        if not field_model:
            return

        query.add_series(series_id, field_model, rep_mode, collapse_agg)

    def _get_model(self, series_id, rep_mode):
        """Valida si el 'series_id' es válido, es decir, si la serie
        pedida es un ID contenido en la base de datos. De no
        encontrarse, llena la lista de errores según corresponda.
        """
        field_model = Field.objects.filter(series_id=series_id)
        if not field_model:
            self._append_error(SERIES_DOES_NOT_EXIST.format(series_id))
            return

        if rep_mode not in constants.REP_MODES:
            error = strings.INVALID_PARAMETER.format(constants.PARAM_REP_MODE,
                                                     rep_mode)
            self._append_error(error)
            return

        return field_model[0]

    def _parse_single_series(self, serie):
        """Parsea una serie invididual. Actualiza la lista de errores
            en caso de encontrar alguno, y la lista de operaciones de collapse
        Args:
            serie (str): string con formato de tipo 'id:rep_mode'

        Returns:
            nombre y rep_mode parseados
        """

        # rep_mode 'default', para todas las series, overrideado
        # si la serie individual especifica alguno
        agg = constants.API_DEFAULT_VALUES[constants.PARAM_COLLAPSE_AGG]
        colon_index = serie.find(':')
        if colon_index < 0:
            name = serie
            rep_mode = None
        else:
            rep_mode = None
            try:
                parts = serie.split(':')

                if len(parts) > 3:
                    return None, None, None
                name = parts[0]
                for part in parts[1:]:
                    if part in constants.REP_MODES and rep_mode is None:
                        rep_mode = part
                    elif part in constants.AGGREGATIONS:
                        agg = part
                    else:
                        return None, None, None

            except ValueError:
                return None, None, None

        return name, rep_mode, agg


class Collapse(BaseOperation):
    """Maneja las distintas agregaciones (suma, promedio)"""
    def run(self, query, args):
        collapse = args.get(constants.PARAM_COLLAPSE)
        if not collapse:
            return

        if collapse not in constants.COLLAPSE_INTERVALS:
            msg = strings.INVALID_PARAMETER.format(constants.PARAM_COLLAPSE,
                                                   collapse)
            self._append_error(msg)
            return

        try:
            query.add_collapse(collapse=collapse)
        except CollapseError:
            msg = strings.INVALID_COLLAPSE.format(collapse)
            self._append_error(msg)


class Metadata(BaseOperation):

    def run(self, query, args):
        metadata = args.get(constants.PARAM_METADATA)
        if not metadata:
            return

        if metadata not in constants.METADATA_SETTINGS:
            msg = strings.INVALID_PARAMETER.format(constants.PARAM_METADATA, metadata)
            self._append_error(msg)
        else:
            query.set_metadata_config(metadata)


class Sort(BaseOperation):

    def run(self, query, args):
        sort = args.get(constants.PARAM_SORT, constants.API_DEFAULT_VALUES[constants.PARAM_SORT])

        if sort not in constants.SORT_VALUES:
            msg = strings.INVALID_PARAMETER.format(constants.PARAM_SORT, sort)
            self._append_error(msg)
        else:
            query.sort(sort)


class Format(BaseOperation):
    """Valida el parámetro de formato de la respuesta. No realiza
    operación
    """
    def run(self, query, args):
        sort = args.get(constants.PARAM_FORMAT,
                        constants.API_DEFAULT_VALUES[constants.PARAM_FORMAT])

        if sort not in constants.FORMAT_VALUES:
            msg = strings.INVALID_PARAMETER.format(constants.PARAM_FORMAT, format)
            self._append_error(msg)


class Header(BaseOperation):
    """Valida el parámetro de header de la respuesta CSV. No realiza
    operación"""

    def run(self, query, args):
        header = args.get(constants.PARAM_HEADER, constants.API_DEFAULT_VALUES[constants.PARAM_HEADER])

        if header not in constants.VALID_CSV_HEADER_VALUES:
            msg = strings.INVALID_PARAMETER.format(constants.PARAM_HEADER, header)
            self._append_error(msg)
