import csv
from typing import Callable
import pandas as pd

from django.conf import settings
from django_datajsonar.models import Field, Distribution

from series_tiempo_ar_api.apps.dump.models import CSVDumpTask
from series_tiempo_ar_api.apps.management import meta_keys


class CsvDumpWriter:
    """Escribe dumps de .csv de *datos*, iterando sobre las distribuciones de los fields pasados,
    y escribiendo un row por cada valor individual (par índice de tiempo - observación) de cada serie.
    El formato de cada row es especificado a través del callable rows.
    """

    def __init__(self, task: CSVDumpTask, fields: dict, rows: Callable):
        self.task = task
        self.fields = fields

        # Funcion generadora de rows, especifica la estructura de la fila
        # a partir de argumentos pasados desde un pandas.apply
        self.rows = rows

    def write(self, filepath, header):
        distribution_ids = Field.objects.filter(
            enhanced_meta__key=meta_keys.AVAILABLE,
        ).values_list('distribution', flat=True)

        with open(filepath, mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for distribution in Distribution.objects.filter(id__in=distribution_ids).order_by('identifier'):
                self.write_distribution(distribution, writer)

    def write_distribution(self, distribution: Distribution, writer: csv.writer):
        # noinspection PyBroadException
        try:
            df = pd.read_csv(distribution.data_file.file,
                             index_col=settings.INDEX_COLUMN,
                             parse_dates=[settings.INDEX_COLUMN])
            fields = distribution.field_set.all()
            fields = {field.title: field.identifier for field in fields}

            df.apply(self.write_serie, args=(distribution, fields, writer))
        except Exception as e:
            CSVDumpTask.info(self.task, f'Error en la distribución {distribution.identifier}: {e.__class__}: {e}')

    def write_serie(self, serie: pd.Series, distribution: Distribution, fields: dict, writer: csv.writer):
        field_id = fields[serie.name]
        df = serie.reset_index().apply(self.rows,
                                       axis=1,
                                       args=(self.fields, field_id, meta_keys.get(distribution, meta_keys.PERIODICITY)))

        serie = pd.Series(df.values, index=serie.index)
        for row in serie:
            writer.writerow(row)
