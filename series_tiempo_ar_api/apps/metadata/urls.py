#!coding=utf8
from django.conf.urls import url

from .views import search, dataset_source

urlpatterns = [
    url('^$', search, name='search'),
    url('^dataset_source$', dataset_source, name='dataset_source')
]
