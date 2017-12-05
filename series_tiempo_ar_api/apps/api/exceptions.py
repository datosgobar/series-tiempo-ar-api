#! coding: utf-8

from .query.strings import END_OF_PERIOD_ERROR


class CollapseError(BaseException):
    pass


class InvalidFormatError(BaseException):
    pass


class QueryError(BaseException):
    pass


class EndOfPeriodError(BaseException):
    message = END_OF_PERIOD_ERROR
