#!coding=utf8
from django.db import models
from django.conf import settings
from django_datajsonar.models import AbstractTask, Node
from minio_storage.storage import MinioMediaStorage, create_minio_client_from_settings
from . import constants


class GenerateDumpTask(AbstractTask):
    TYPE_CSV = 'csv'
    TYPE_XLSX = 'xlsx'
    TYPE_CHOICES = (
        (TYPE_CSV, 'CSV'),
        (TYPE_XLSX, 'XLSX'),
    )

    file_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='CSV')


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
    TYPE_CHOICES = (
        (TYPE_CSV, 'CSV'),
        (TYPE_XLSX, 'XLSX'),
        (TYPE_ZIP, 'ZIP'),
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

    @classmethod
    def get_from_path(cls, filename: str, node: str = None) -> 'DumpFile':
        """Devuelve la última instancia de clase que corresponda al archivo con filename de formato tipo
        <catalog>/<file_name>.<extension>. Lanza DoesNotExist si no se encuentra un dump correspondiente.
        """

        try:
            name, extension = filename.split('.')
        except ValueError:
            raise cls.DoesNotExist

        try:
            node = Node.objects.get(catalog_id=node) if node else None
        except Node.DoesNotExist:
            raise cls.DoesNotExist

        dump = cls.objects.filter(file_name=name, file_type=extension, node=node).last()
        if dump is None:
            raise cls.DoesNotExist
        return dump
