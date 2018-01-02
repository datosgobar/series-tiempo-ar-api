from django.conf.urls import url

from .views import save

urlpatterns = [
    url('^save/$', save, name='save')
]
