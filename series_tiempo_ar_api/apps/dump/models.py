#!coding=utf8
import os
import zipfile

from django.core.files import File
from django.db import models
from django.conf import settings
from minio_storage.storage import MinioMediaStorage, create_minio_client_from_settings
from django_datajsonar.models import AbstractTask, Node
from . import constants


class GenerateDumpTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de generación de dumps"
        verbose_name = "Corrida de generación de dumps"

    TYPE_DTA = 'dta'
    TYPE_SQL = 'sql'
    TYPE_CSV = 'csv'
    TYPE_XLSX = 'xlsx'
    TYPE_CHOICES = (
        (TYPE_CSV, 'CSV'),
        (TYPE_XLSX, 'XLSX'),
        (TYPE_SQL, 'SQL'),
        (TYPE_DTA, 'DTA'),
    )

    file_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='CSV')

    def delete(self, using=None, keep_parents=False):
        for dump in self.dumpfile_set.all():
            dump.delete()

        return super(GenerateDumpTask, self).delete(using, keep_parents)


def dumpfile_upload_to(dump_file, _):
    directory = f'{dump_file.node}/' or ''
    return f'dump/{directory}{dump_file.file_name}.{dump_file.file_type}'


class DumpFile(models.Model):

    file = models.FileField(upload_to=dumpfile_upload_to, storage=MinioMediaStorage())

    FILENAME_FULL = 'series-tiempo'
    FILENAME_VALUES = 'series-tiempo-valores'
    FILENAME_METADATA = 'series-tiempo-metadatos'
    FILENAME_SOURCES = 'series-tiempo-fuentes'
    FILENAME_CHOICES = (
        (FILENAME_FULL, 'Series de tiempo (valores + metadatos)'),
        (FILENAME_VALUES, 'Series de tiempo (valores)'),
        (FILENAME_METADATA, 'Series de tiempo (metadatos)'),
        (FILENAME_SOURCES, 'Series de tiempo (fuentes)'),
    )
    file_name = models.CharField(max_length=64, choices=FILENAME_CHOICES)

    TYPE_CSV = 'csv'
    TYPE_XLSX = 'xlsx'
    TYPE_ZIP = 'zip'
    TYPE_SQL = 'sqlite'
    TYPE_DTA = 'dta'

    TYPE_CHOICES = (
        (TYPE_CSV, 'CSV'),
        (TYPE_XLSX, 'XLSX'),
        (TYPE_ZIP, 'ZIP'),
        (TYPE_SQL, 'SQL'),
        (TYPE_DTA, 'DTA'),
    )

    ZIP_FILES = (
        (FILENAME_FULL, TYPE_CSV),
        (FILENAME_VALUES, TYPE_CSV),
        (FILENAME_FULL, TYPE_SQL),
        (FILENAME_VALUES, TYPE_DTA),
    )

    file_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default=TYPE_CSV)

    task = models.ForeignKey(GenerateDumpTask, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.PROTECT, blank=True, null=True)

    def delete(self, using=None, keep_parents=False):
        if self.file:
            minio = create_minio_client_from_settings()
            minio.remove_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, self.file.name)
        super(DumpFile, self).delete(using, keep_parents)

    def get_path(self):
        directory = f'{self.node.catalog_id}/' if self.node else ''
        return f'{constants.DUMP_DIR}/{directory}{self.get_file_name()}'

    def get_file_name(self):
        return f'{self.file_name}.{self.file_type}'

    def __str__(self):
        return f'{self.get_file_name()} ({self.node or "global"})'

    @classmethod
    def get_from_path(cls, filename: str, node: str = None) -> 'DumpFile':
        """Devuelve la última instancia de clase que corresponda al archivo con filename de formato tipo
        <catalog>/<file_name>.<extension>. Lanza DoesNotExist si no se encuentra un dump correspondiente.
        """

        try:
            node = Node.objects.get(catalog_id=node) if node else None
        except Node.DoesNotExist:
            raise cls.DoesNotExist

        try:
            name, extension = filename.split('.')
        except ValueError:
            raise cls.DoesNotExist

        if extension == cls.TYPE_ZIP:
            split = name.rfind('-')
            orig_extension = name[split + 1:]
            name = name[:split]
            dump = cls.objects.filter(file_name=name, file_type=orig_extension, node=node).last()
            try:
                return ZipDumpFile.objects.get(dump_file=dump)
            except ZipDumpFile.DoesNotExist:
                raise cls.DoesNotExist

        dump = cls.objects.filter(file_name=name, file_type=extension, node=node).last()

        if dump is None:
            raise cls.DoesNotExist
        return dump

    @classmethod
    def get_last_of_type(cls, file_type: str, node: str = None) -> list:
        """Devuelve el último dump generado del formato file_type especificado.
        Si se pasa un parámetro node, devuelve los últimos dumps para ese node.
        Si no, se devuelve los últimos dumps globales.
        """

        dumps_qs = cls.objects.filter(node__catalog_id=node)

        dumps = []
        for dump_name, _ in cls.FILENAME_CHOICES:
            dump_file = dumps_qs.filter(file_name=dump_name, file_type=file_type).last()
            if dump_file is not None:
                dumps.append(dump_file)

        return dumps


def zipfile_upload_to(instance: 'ZipDumpFile', _):
    dump_file = instance.dump_file
    directory = f'{dump_file.node}/' or ''
    return f'dump/{directory}{dump_file.file_name}-{dump_file.file_type}.zip'


class ZipDumpFile(models.Model):
    dump_file = models.ForeignKey(DumpFile, on_delete=models.CASCADE)
    file = models.FileField(upload_to=zipfile_upload_to, storage=MinioMediaStorage())

    @classmethod
    def create_from_dump_file(cls, dump_file: DumpFile, dump_file_path: str):

        with TempZipDumpFile(dump_file) as zip_file:
            zip_file.write(dump_file_path, arcname=f'{dump_file.file_name}.{dump_file.file_type}')
            zip_file.close()

            with open(zip_file.filename, 'rb') as f:
                return cls.objects.create(file=File(f),
                                          dump_file=dump_file)

    def delete(self, using=None, keep_parents=False):
        if self.file:
            minio = create_minio_client_from_settings()
            minio.remove_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, self.file.name)
        super(ZipDumpFile, self).delete(using, keep_parents)


class TempZipDumpFile:
    def __init__(self, dump_file):
        self.filepath = f'{dump_file.file_name}-{dump_file.file_type}-{dump_file.id}.zip'
        self.zipfile = None

    def __enter__(self):
        self.remove_if_exists()
        self.zipfile = zipfile.ZipFile(self.filepath, 'w', zipfile.ZIP_DEFLATED)
        return self.zipfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.zipfile.fp:
            self.zipfile.close()

        self.remove_if_exists()

    def remove_if_exists(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
