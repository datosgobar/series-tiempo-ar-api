#!coding:utf-8
import os

import sendfile
from django.conf import settings


def serve_global_dump(request, filename):

    path = os.path.join(settings.MEDIA_ROOT, filename)
    return sendfile.sendfile(request, path)
