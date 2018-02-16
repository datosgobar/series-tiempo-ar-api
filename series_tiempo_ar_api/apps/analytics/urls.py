from django.conf.urls import url
from .views import save, read_analytics

urlpatterns = [
    url('^save/$', save, name='save'),
    url('^analytics.csv', read_analytics, name='read_analytics'),
]
