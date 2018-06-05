#!coding=utf8

from django.conf.urls import url

from .views import serve_global_dump
from . import constants


files_re = r'^(?P<filename>' + '|'.join(constants.FILES) + ')$'

urlpatterns = [
    url(files_re, serve_global_dump, name='global_dump'),
]
