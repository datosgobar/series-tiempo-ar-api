#!coding:utf-8
import os

import sendfile
from django.conf import settings


def test_view(request, filename):

    path = os.path.join(settings.MEDIA_ROOT, filename)
    return sendfile.sendfile(request, path)
