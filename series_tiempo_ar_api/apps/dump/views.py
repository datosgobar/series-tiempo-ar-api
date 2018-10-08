#!coding:utf-8
from urllib.parse import urlparse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from minio_storage.storage import create_minio_client_from_settings

from .models import DumpFile
from .constants import DUMP_ERROR, DUMPS_NOT_GENERATED


def serve_global_dump(_, filename):
    return serve_dump_file(filename)


def serve_catalog_dump(_, catalog_id, filename):
    full_file_name = f'{catalog_id}/{filename}'

    return serve_dump_file(full_file_name)


def serve_dump_file(filename: str) -> HttpResponse:
    name, ext = filename.split('.')
    dump_file = DumpFile.objects.filter(file_name=name,
                                        file_type=ext).last()
    if dump_file is None:
        return HttpResponse(DUMPS_NOT_GENERATED, status=501)  # "Not implemented"

    if dump_file.file is None:
        return HttpResponse(DUMP_ERROR, status=500)

    conn = create_minio_client_from_settings()
    response = conn.presigned_get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                         dump_file.file.name)

    # Devuelvo el archivo desde nginx, de estar configurado
    if getattr(settings, 'MINIO_SERVE_FILES_URL', None):
        parsed = urlparse(response)
        return redirect(f'{settings.MINIO_SERVE_FILES_URL}{parsed.path}?{parsed.query}')

    return HttpResponseRedirect(response)
