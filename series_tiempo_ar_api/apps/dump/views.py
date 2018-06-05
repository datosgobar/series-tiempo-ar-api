#!coding:utf-8
import sendfile
from django.http import HttpResponse
from .models import DumpFile
from .constants import DUMP_ERROR, DUMPS_NOT_GENERATED


def serve_global_dump(request, filename):
    dump_file = DumpFile.objects.filter(file_name=filename).last()
    if dump_file is None:
        return HttpResponse(DUMPS_NOT_GENERATED, status=501)  # "Not implemented"
    dump_file = dump_file.file

    if dump_file is None:
        return HttpResponse(DUMP_ERROR, status=500)
    return sendfile.sendfile(request, dump_file.path)
