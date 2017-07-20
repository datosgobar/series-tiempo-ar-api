#! coding: utf-8
from django.conf.urls import url

from elastic_spike.apps.api.views import All, Oferta

urlpatterns = [
    url('^all/$', All.as_view()),
    url('^search/$', Oferta.as_view())
]
