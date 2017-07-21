#! coding: utf-8
from django.conf.urls import url

from elastic_spike.apps.api.views import All, SearchAPI

urlpatterns = [
    url('^all/$', All.as_view()),
    url('^search/$', SearchAPI.as_view()),
    url('^search/(?P<series>[a-z, _]+)/$', SearchAPI.as_view())
]
