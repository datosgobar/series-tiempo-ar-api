#! coding: utf-8
from django.conf.urls import url

from series_tiempo_ar_api.apps.api.views import query_view, save_request

urlpatterns = [
    url('^series/$', query_view, name='series'),
    url('^analytics/$', save_request, name='save_request')
]
