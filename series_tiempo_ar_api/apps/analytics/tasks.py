#! coding: utf-8
import requests
from django_rq import job
from .importer import AnalyticsImporter


def enqueue_new_import_analytics_task(limit=1000, requests_lib=requests, import_all=False, index_to_es=True):
    AnalyticsImporter(limit=limit, requests_lib=requests_lib, index_to_es=index_to_es).run(import_all)


@job('analytics', timeout=1000)
def import_analytics(task, limit=1000, requests_lib=requests, import_all=False, index_to_es=True):
    AnalyticsImporter(task=task, limit=limit, requests_lib=requests_lib, index_to_es=index_to_es).run(import_all)
