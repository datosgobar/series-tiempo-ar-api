# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = [url(r'^admin/', include(admin.site.urls)),
               url(r'', include('elastic_spike.apps.api.urls', namespace="api"))] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
