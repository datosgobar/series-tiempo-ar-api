#! coding: utf-8

from django_rq import job
from ..models import Query


@job("default")
def analytics(ids, args):
    query = Query(ids=ids, args=args)
    query.save()
