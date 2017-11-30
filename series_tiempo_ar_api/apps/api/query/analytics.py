#! coding: utf-8
import json
from django_rq import job
from ..models import Query


@job("default")
def analytics(ids, args_string, ip_address, args):
    args_json = json.dumps(args)
    query = Query(ids=ids, args=args_string, ip_address=ip_address, params=args_json)
    query.save()
