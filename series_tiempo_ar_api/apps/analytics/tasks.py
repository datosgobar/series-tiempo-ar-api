#! coding: utf-8
import datetime

import requests
from dateutil.relativedelta import relativedelta
from django_rq import job

from series_tiempo_ar_api.apps.analytics.elasticsearch.indicators import calculate_hits_indicators
from .importer import AnalyticsImporter


@job('analytics')
def enqueue_new_import_analytics_task(limit=1000, requests_lib=requests, import_all=False, index_to_es=True, **_):
    AnalyticsImporter(limit=limit, requests_lib=requests_lib, index_to_es=index_to_es).run(import_all)


@job('analytics', timeout=-1)
def import_analytics(task, limit=1000, requests_lib=requests, import_all=False, index_to_es=True):
    AnalyticsImporter(task=task, limit=limit, requests_lib=requests_lib, index_to_es=index_to_es).run(import_all)


@job('hits_indicators', timeout=-1)
def enqueue_new_calculate_hits_indicators_task(*_):
    yesterday = datetime.date.today() - relativedelta(days=1)
    calculate_hits_indicators(for_date=yesterday)
