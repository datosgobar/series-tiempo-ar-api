#! coding: utf-8
from django.conf.urls import url

from series_tiempo_ar_api.apps.validator.views import ValidatorView

urlpatterns = [
    url('^$', ValidatorView.as_view(), name='validator'),
]
