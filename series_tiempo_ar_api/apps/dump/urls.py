#!coding=utf8

from django.conf.urls import url

from .views import test_view
from . import constants


files_re = r'^(?P<filename>' + '|'.join(constants.FILES) + ')$'

urlpatterns = [
    url(files_re, test_view, name='dump'),
]