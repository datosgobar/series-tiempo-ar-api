#!coding=utf8
from django.conf.urls import url

from .views import query

urlpatterns = [
    url('^search/$', query, name='search'),
]
