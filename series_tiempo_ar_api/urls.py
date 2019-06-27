# coding=utf-8
from __future__ import unicode_literals

import django_datajsonar.urls
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from des import urls as des_urls
from django.contrib.auth import views as auth_views


admin.autodiscover()
admin.site.index_template = "custom_index.html"

api_endpoints = [
    url(r'series/', include('series_tiempo_ar_api.apps.api.urls', namespace="series")),
    url(r'search/', include('series_tiempo_ar_api.apps.metadata.urls', namespace='metadata')),
    url(r'dump/', include('series_tiempo_ar_api.apps.dump.urls', namespace='dump')),
]

urlpatterns = [

    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^api/', include(api_endpoints, namespace="api")),
    url(r'^analytics/', include('series_tiempo_ar_api.apps.analytics.urls', namespace='analytics')),
    url(r'^django-des/', include(des_urls)),
    url(r'^', include(django_datajsonar.urls)),
    url(r'^admin/password_reset/$', auth_views.PasswordResetView.as_view(),
        name='admin_password_reset',),
    url(r'^admin/password_reset/done/$',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
