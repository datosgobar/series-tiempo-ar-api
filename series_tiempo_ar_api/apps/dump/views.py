#!coding:utf-8
from urllib.parse import urlparse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from minio_storage.storage import create_minio_client_from_settings

from .models import DumpFile
from .constants import DUMP_ERROR


def serve_global_dump(_, filename):
    return serve_dump_file(filename)


def serve_catalog_dump(_, catalog_id, filename):
    return serve_dump_file(filename, catalog_id)


def serve_dump_file(filename: str, catalog: str = None) -> HttpResponse:
    try:
        dump_file = DumpFile.get_from_path(filename, catalog)
    except DumpFile.DoesNotExist:
        raise Http404

    if dump_file.file is None:
        return HttpResponse(DUMP_ERROR, status=500)

    conn = create_minio_client_from_settings()

    # Devuelvo el archivo desde nginx, de estar configurado
    if getattr(settings, 'MINIO_SERVE_FILES_URL', None):
        headers = {'response-content-disposition': f'attachment; filename="{filename}"'}
        response = conn.presigned_get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                             dump_file.file.name,
                                             response_headers=headers)

        parsed = urlparse(response)
        response = redirect(f'{settings.MINIO_SERVE_FILES_URL}{parsed.path}?{parsed.query}')
        response['Content-Disposition'] = f"attachment; {filename}"
        return redirect(f'{settings.MINIO_SERVE_FILES_URL}{parsed.path}?{parsed.query}')

    response = conn.presigned_get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                         dump_file.file.name)

    return HttpResponseRedirect(response)
