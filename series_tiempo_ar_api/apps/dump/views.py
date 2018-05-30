#!coding:utf-8
import os

import sendfile
from . import constants


def serve_global_dump(request, filename):

    path = os.path.join(constants.DUMP_DIR, filename)
    return sendfile.sendfile(request, path)
