#!coding=utf8

from django.conf.urls import url

from .views import serve_global_dump, serve_catalog_dump
from . import constants


files_re = r'(?P<filename>' + '|'.join(constants.FILES) + ')$'

urlpatterns = [
    url(r'^' + files_re, serve_global_dump, name='global_dump'),
    url(r'^(?P<catalog_id>.*)/' + files_re, serve_catalog_dump, name='catalog_dump')
]
