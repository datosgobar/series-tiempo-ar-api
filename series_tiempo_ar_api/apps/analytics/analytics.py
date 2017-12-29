#! coding: utf-8
import json
from django_rq import job
from .models import Query


@job("default")
def analytics(ids, args_string, ip_address, params):
    params_json = json.dumps(params)
    query = Query(ids=ids, args=args_string, ip_address=ip_address, params=params_json)
    query.save()
