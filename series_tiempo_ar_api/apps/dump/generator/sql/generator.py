import os

import peewee
from django.core.files import File
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.generator.metadata import MetadataCsvGenerator
from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask
from series_tiempo_ar_api.utils import read_file_as_csv

proxy = peewee.Proxy()


class Serie(peewee.Model):
    class Meta:
        database = proxy

    catalogo_id = peewee.CharField(max_length=64)
    dataset_id = peewee.CharField(max_length=128)
    distribucion_id = peewee.CharField(max_length=128)
    serie_id = peewee.CharField(max_length=128)
    indice_tiempo_frecuencia = peewee.CharField(max_length=8)
    titulo = peewee.TextField()
    unidades = peewee.TextField()
    descripcion = peewee.TextField()
    indice_inicio = peewee.DateField()
    indice_final = peewee.DateField()
    valores_cant = peewee.IntegerField(null=True)
    dias_no_cubiertos = peewee.IntegerField(null=True)


class Distribucion(peewee.Model):
    class Meta:
        database = proxy

    catalogo_id = peewee.CharField(max_length=64)
    dataset_id = peewee.CharField(max_length=128)
    identifier = peewee.CharField(max_length=128)
    titulo = peewee.TextField()
    descripcion = peewee.TextField()


class Dataset(peewee.Model):
    class Meta:
        database = proxy

    catalogo_id = peewee.CharField(max_length=64)
    identifier = peewee.CharField(max_length=128)
    titulo = peewee.TextField()
    descripcion = peewee.TextField()
    fuente = peewee.TextField()
    responsable = peewee.TextField()


class Valores(peewee.Model):
    class Meta:
        database = proxy

    serie_id = peewee.CharField(max_length=128)
    indice_tiempo = peewee.DateField()
    valor = peewee.DoubleField()


class SQLGenerator:
    metadata_rows = MetadataCsvGenerator.rows

    def __init__(self, task_id: int, catalog_id: str = None):
        self.task = GenerateDumpTask.objects.get(id=task_id)
        self.node = Node.objects.get(catalog_id=catalog_id) if catalog_id else None
        self.covered_datasets = set()
        self.covered_distributions = set()

        self.cols = {}
        self.series = []
        self.datasets = []
        self.distributions = []

    def generate(self):

        meta = DumpFile.objects.get(node=self.node,
                                    file_name=DumpFile.FILENAME_METADATA,
                                    file_type=DumpFile.TYPE_CSV)

        if meta.file is None:
            return

        reader = read_file_as_csv(meta.file)
        next(reader)  # Skip header
        self.init_sql()

        for row in reader:
            self.init_dataset(row)
            self.init_distribution(row)
            self.init_serie(row)

        Dataset.bulk_create(self.datasets)
        Distribucion.bulk_create(self.distributions)
        Serie.bulk_create(self.series)

        with open(self.db_name(), 'rb') as f:
            self.task.dumpfile_set.create(node=self.node,
                                          file=File(f),
                                          file_type=DumpFile.TYPE_SQL,
                                          file_name=DumpFile.FILENAME_FULL)

        os.remove(self.db_name())

    def init_sql(self):
        name = self.db_name()
        db = peewee.SqliteDatabase(name)
        proxy.initialize(db)
        db.create_tables([Serie, Distribucion, Dataset, Valores])

    def init_dataset(self, row: list):
        dataset_id = row[self.metadata_rows.index('dataset_id')]
        if dataset_id in self.covered_datasets:
            return
        catalog_id = row[self.metadata_rows.index('catalogo_id')]
        title = row[self.metadata_rows.index('dataset_titulo')]
        description = row[self.metadata_rows.index('dataset_descripcion')]
        source = row[self.metadata_rows.index('dataset_fuente')]
        publisher = row[self.metadata_rows.index('dataset_responsable')]

        self.datasets.append(Dataset.create(
            catalogo_id=catalog_id,
            identifier=dataset_id,
            titulo=title,
            descripcion=description,
            fuente=source,
            responsable=publisher
        ))
        self.covered_datasets.add(dataset_id)

    def init_distribution(self, row: list):
        distribution_id = row[self.metadata_rows.index('distribucion_id')]
        if distribution_id in self.covered_distributions:
            return

        dataset_id = row[self.metadata_rows.index('dataset_id')]
        catalog_id = row[self.metadata_rows.index('catalogo_id')]

        title = row[self.metadata_rows.index('distribucion_titulo')]
        description = row[self.metadata_rows.index('distribucion_descripcion')]

        self.distributions.append(Distribucion(
            catalogo_id=catalog_id,
            dataset_id=dataset_id,
            identifier=distribution_id,
            titulo=title,
            descripcion=description,
        ))
        self.covered_distributions.add(distribution_id)

    def init_serie(self, row: list):
        serie_id = row[self.metadata_rows.index('serie_id')]
        distribution_id = row[self.metadata_rows.index('distribucion_id')]
        dataset_id = row[self.metadata_rows.index('dataset_id')]
        catalog_id = row[self.metadata_rows.index('catalogo_id')]
        frequency = row[self.metadata_rows.index('indice_tiempo_frecuencia')]
        title = row[self.metadata_rows.index('serie_titulo')]
        units = row[self.metadata_rows.index('serie_unidades')]
        description = row[self.metadata_rows.index('serie_descripcion')]
        index_start = row[self.metadata_rows.index('serie_indice_inicio')]
        index_end = row[self.metadata_rows.index('serie_indice_final')]
        value_count = row[self.metadata_rows.index('serie_valores_cant')] or 0
        days_not_covered = row[self.metadata_rows.index('serie_dias_no_cubiertos')] or 0

        self.series.append(Serie(
            catalogo_id=catalog_id,
            dataset_id=dataset_id,
            distribucion_id=distribution_id,
            serie_id=serie_id,
            indice_tiempo_frecuencia=frequency,
            titulo=title,
            unidades=units,
            descripcion=description,
            indice_inicio=index_start,
            indice_final=index_end,
            valores_cant=value_count,
            dias_no_cubiertos=days_not_covered,
        ))

    def db_name(self):
        name = self.node.catalog_id if self.node else 'global'
        return f'{name}.sqlite'
