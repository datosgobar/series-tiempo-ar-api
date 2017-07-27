#! coding: utf-8
from django.conf.urls import url

from elastic_spike.apps.api.views import SearchAPI

urlpatterns = [
    url('^search/$', SearchAPI.as_view()),
    url('^search/(?P<series>.+)/$', SearchAPI.as_view())
]
