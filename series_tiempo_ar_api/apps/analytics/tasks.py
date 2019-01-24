#! coding: utf-8
import requests
from django_rq import job
from .importer import AnalyticsImporter


def enqueue_new_import_analytics_task(limit=1000, requests_lib=requests, import_all=False):
    AnalyticsImporter(limit=limit, requests_lib=requests_lib).run(import_all)


@job('default', timeout=1000)
def import_analytics(task, limit=1000, requests_lib=requests, import_all=False):
    AnalyticsImporter(task=task, limit=limit, requests_lib=requests_lib).run(import_all)
