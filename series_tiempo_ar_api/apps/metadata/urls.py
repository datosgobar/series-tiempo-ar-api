#!coding=utf8
from django.conf.urls import url

from .views import search

urlpatterns = [
    url('^$', search, name='search'),
]
