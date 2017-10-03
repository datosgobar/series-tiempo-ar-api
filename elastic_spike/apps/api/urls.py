#! coding: utf-8
from django.conf.urls import url

from elastic_spike.apps.api.views import query_view

urlpatterns = [
    url('^series/$', query_view)
]
