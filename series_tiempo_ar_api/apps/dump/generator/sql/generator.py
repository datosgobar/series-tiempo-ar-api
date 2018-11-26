import os

import peewee
from django.core.files import File
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.constants import VALUES_HEADER
from series_tiempo_ar_api.apps.dump.generator import constants
from series_tiempo_ar_api.apps.dump.generator.sources import SourcesCsvGenerator
from series_tiempo_ar_api.apps.dump.generator.sql.models import Metadatos, Valores, proxy, Fuentes
from series_tiempo_ar_api.apps.dump.generator.xlsx.formats import bool_format
from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask, ZipDumpFile
from series_tiempo_ar_api.utils.utils import read_file_as_csv


class SQLGenerator:
    metadata_rows = constants.METADATA_ROWS
    values_rows = VALUES_HEADER
    sources_rows = SourcesCsvGenerator.columns

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
        with DbWrapper(self.db_name()):
            self.write_metadata_tables()
            self.write_sources_table()
            self.write_values_table()

            with open(self.db_name(), 'rb') as f:
                dump_file = self.task.dumpfile_set.create(node=self.node,
                                                          file=File(f),
                                                          file_type=DumpFile.TYPE_SQL,
                                                          file_name=DumpFile.FILENAME_FULL)

                ZipDumpFile.create_from_dump_file(dump_file, self.db_name())

    def write_metadata_tables(self):
        meta = DumpFile.objects.filter(node=self.node,
                                       file_name=DumpFile.FILENAME_METADATA,
                                       file_type=DumpFile.TYPE_CSV).last()

        if meta is None or meta.file is None:
            return

        reader = read_file_as_csv(meta.file)
        next(reader)  # Skip header

        Metadatos.bulk_create(self.generate_series_rows(reader), batch_size=100)

    def generate_series_rows(self, reader):
        for row in reader:
            catalog_id = row[self.metadata_rows.index(constants.CATALOG_ID)]
            dataset_id = row[self.metadata_rows.index(constants.DATASET_ID)]
            distribution_id = row[self.metadata_rows.index(constants.DISTRIBUTION_ID)]
            serie_id = row[self.metadata_rows.index(constants.SERIE_ID)]
            frequency = row[self.metadata_rows.index(constants.TIME_INDEX_FREQUENCY)]
            title = row[self.metadata_rows.index(constants.SERIES_TITLE)]
            units = row[self.metadata_rows.index(constants.SERIES_UNITS)]
            description = row[self.metadata_rows.index(constants.SERIES_DESCRIPTION)]

            distribution_title = row[self.metadata_rows.index(constants.DISTRIBUTION_TITLE)]
            distribution_description = row[self.metadata_rows.index(constants.SERIES_DESCRIPTION)]
            distribution_download_url = row[self.metadata_rows.index(constants.DISTRIBUTION_DOWNLOAD_URL)]

            dataset_title = row[self.metadata_rows.index(constants.DATASET_THEME)]
            dataset_description = row[self.metadata_rows.index(constants.DATASET_DESCRIPTION)]
            dataset_source = row[self.metadata_rows.index(constants.DATASET_SOURCE)]
            dataset_publisher = row[self.metadata_rows.index(constants.DATASET_PUBLISHER)]
            dataset_theme = row[self.metadata_rows.index(constants.DATASET_THEME)]

            index_start = row[self.metadata_rows.index(constants.SERIES_INDEX_START)]
            index_end = row[self.metadata_rows.index(constants.SERIES_INDEX_END)]
            value_count = row[self.metadata_rows.index(constants.SERIES_VALUES_AMT)] or 0
            days_not_covered = row[self.metadata_rows.index(constants.SERIES_DAYS_SINCE_LAST_UPDATE)] or 0
            is_updated = bool_format(row[self.metadata_rows.index(constants.SERIES_IS_UPDATED)])
            last_value = row[self.metadata_rows.index(constants.SERIES_LAST_VALUE)]
            second_last_value = row[self.metadata_rows.index(constants.SERIES_SECOND_LAST_VALUE)] or 0
            last_pct_change = row[self.metadata_rows.index(constants.SERIES_PCT_CHANGE)] or 0

            yield Metadatos(
                catalogo_id=catalog_id,
                dataset_id=dataset_id,
                distribucion_id=distribution_id,
                serie_id=serie_id,
                indice_tiempo_frecuencia=frequency,
                serie_titulo=title,
                serie_unidades=units,
                serie_descripcion=description,
                distribucion_titulo=distribution_title,
                distribucion_descripcion=distribution_description,
                distribucion_url_descarga=distribution_download_url,
                dataset_responsable=dataset_publisher,
                dataset_fuente=dataset_source,
                dataset_titulo=dataset_title,
                dataset_descripcion=dataset_description,
                dataset_tema=dataset_theme,
                serie_indice_inicio=index_start,
                serie_indice_final=index_end,
                serie_valores_cant=value_count,
                serie_dias_no_cubiertos=days_not_covered,
                serie_actualizada=is_updated,
                serie_valor_ultimo=last_value,
                serie_valor_anterior=second_last_value,
                serie_var_pct_anterior=last_pct_change,
            )

    def db_name(self):
        name = self.node.catalog_id if self.node else 'global'
        return f'{name}.sqlite'

    def write_values_table(self):
        values = DumpFile.objects.filter(file_name=DumpFile.FILENAME_VALUES,
                                         file_type=DumpFile.TYPE_CSV,
                                         node=self.node).last()
        if values is None or values.file is None:
            return

        reader = read_file_as_csv(values.file)
        next(reader)  # Skip header

        Valores.bulk_create(self.generate_values_rows(reader), batch_size=1000)

    def generate_values_rows(self, reader):
        for row in reader:
            index = row[self.values_rows.index('indice_tiempo')]
            serie_id = row[self.values_rows.index('serie_id')]
            value = row[self.values_rows.index('valor')]

            yield Valores(
                serie_id=serie_id,
                indice_tiempo=index,
                valor=value,
            )

    def write_sources_table(self):
        sources = DumpFile.objects.filter(file_name=DumpFile.FILENAME_SOURCES,
                                          file_type=DumpFile.TYPE_CSV,
                                          node=self.node).last()

        if sources is None or sources.file is None:
            return

        reader = read_file_as_csv(sources.file)
        next(reader)  # Skip header

        actions = []
        for row in reader:
            Fuentes(
                fuente=row[self.sources_rows.index('dataset_fuente')],
                series_cant=row[self.sources_rows.index('series_cant')],
                valores_cant=row[self.sources_rows.index('valores_cant')],
                fecha_primer_valor=row[self.sources_rows.index('fecha_primer_valor')],
                fecha_ultimo_valor=row[self.sources_rows.index('fecha_ultimo_valor')],
            ).save()

        if actions:
            Fuentes.bulk_create(actions)


class DbWrapper:

    def __init__(self, name):
        self.name = name
        self.db = None

    def __enter__(self):
        if os.path.exists(self.name):
            os.remove(self.name)

        self.db = peewee.SqliteDatabase(self.name)
        proxy.initialize(self.db)
        self.db.create_tables([Metadatos, Valores, Fuentes])

        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self.name):
            os.remove(self.name)
