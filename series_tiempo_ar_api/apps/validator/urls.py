#! coding: utf-8
from django.conf.urls import url

from series_tiempo_ar_api.apps.validator.views import validator_view

urlpatterns = [
    url('^$', validator_view, name='validator'),
]
