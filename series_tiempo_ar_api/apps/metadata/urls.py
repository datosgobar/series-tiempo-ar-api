#!coding=utf8
from django.conf.urls import url

from .views import search, dataset_source, field_units, \
    dataset_publisher_name, dataset_theme, catalog_id

urlpatterns = [
    url('^$', search, name='search'),
    url('^dataset_source/$', dataset_source, name='dataset_source'),
    url('^field_units/$', field_units, name='field_units'),
    url('^dataset_publisher_name/$', dataset_publisher_name, name='dataset_publisher_name'),
    url('^dataset_theme/$', dataset_theme, name='dataset_theme'),
    url('^catalog_id/$', catalog_id, name='catalog_id'),
]
