#!coding=utf8

from django.conf.urls import url

from .views import serve_global_dump, serve_catalog_dump
from . import constants


urlpatterns = [
    url(r'^(?P<filename>.*)$', serve_global_dump, name='global_dump'),
    url(r'^(?P<catalog_id>.*)/(?P<filename>.*)$', serve_catalog_dump, name='catalog_dump')
]
