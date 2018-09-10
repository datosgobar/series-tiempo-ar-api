#!coding:utf-8
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from minio_storage.storage import create_minio_client_from_settings

from .models import DumpFile
from .constants import DUMP_ERROR, DUMPS_NOT_GENERATED


def serve_global_dump(request, filename):
    dump_file = DumpFile.objects.filter(file_name=filename).last()
    if dump_file is None:
        return HttpResponse(DUMPS_NOT_GENERATED, status=501)  # "Not implemented"

    if dump_file.file is None:
        return HttpResponse(DUMP_ERROR, status=500)

    conn = create_minio_client_from_settings()
    response = conn.presigned_get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                         dump_file.file.name)

    return HttpResponseRedirect(response)
