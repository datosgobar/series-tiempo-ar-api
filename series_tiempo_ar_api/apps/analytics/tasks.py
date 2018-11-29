#! coding: utf-8
import requests
from django_rq import job
from .importer import AnalyticsImporter


@job('default', timeout=1000)
def import_analytics_from_api_mgmt(limit=1000, requests_lib=requests, import_all=False):
    AnalyticsImporter(limit, requests_lib).run(import_all)
