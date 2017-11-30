#! coding: utf-8
import json

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

s = Search(using=Elasticsearch(), index="indicators").filter('match', series_id="3.2_DGE_D_2004_T_26")

s.aggs.bucket('end_of_period', 'date_histogram', field='timestamp', interval='year') \
    .metric('agg', 'scripted_metric',
            init_script="params._agg.last_date = -1; params._agg.value = 0;",
            map_script="if (doc.timestamp.value > params._agg.last_date) { params._agg.last_date = doc.timestamp.value; params._agg.value = doc.value.value; }",
            reduce_script="double value = -1; long last_date = 0; for (a in params._aggs) { if (a != null && a.last_date > last_date) { value = a.value; last_date = a.last_date; } } return value")


r = s.execute()
for hit in r.aggs.end_of_period.buckets:
    print hit.keys()
