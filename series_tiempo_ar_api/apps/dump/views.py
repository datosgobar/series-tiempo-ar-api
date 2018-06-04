#!coding:utf-8
import os

import sendfile
from django.http import HttpResponse
from .models import CSVDumpTask


def serve_global_dump(request, filename):
    task = CSVDumpTask.objects.last()
    if task is None:
        return HttpResponse("Dumps no generados", status=501)  # "Not implemented"
    dump_file = task.dumpfile_set.get(file_name=filename).file

    return sendfile.sendfile(request, dump_file.path)
