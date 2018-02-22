#! coding: utf-8
from django.conf.urls import url

from series_tiempo_ar_api.apps.api.views import query_view

urlpatterns = [
    url('^$', query_view, name='series'),
]
