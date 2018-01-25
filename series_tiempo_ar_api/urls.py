# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from des import urls as des_urls


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^api/', include('series_tiempo_ar_api.apps.api.urls', namespace="api")),
    url(r'^analytics/', include('series_tiempo_ar_api.apps.analytics.urls', namespace='analytics')),
    url(r'^django-des/', include(des_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
