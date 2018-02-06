#! coding: utf-8
from django.utils.timezone import datetime, get_current_timezone


def milliseconds_to_seconds(timestamp):
    return timestamp / 1000


def kong_milliseconds_to_tzdatetime(timestamp):
    return datetime.fromtimestamp(milliseconds_to_seconds(timestamp), get_current_timezone())
