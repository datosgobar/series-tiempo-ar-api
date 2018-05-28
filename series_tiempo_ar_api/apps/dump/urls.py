#!coding=utf8

from django.conf.urls import url

from .views import test_view

urlpatterns = [
    url('^$', test_view, name='dump'),
]