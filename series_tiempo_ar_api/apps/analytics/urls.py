from django.conf.urls import url
from .views import save, export_analytics

urlpatterns = [
    url('^save/$', save, name='save'),
    url('^analytics.csv', export_analytics, name='read_analytics'),
]
