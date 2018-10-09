import logging
import csv
import os
from typing import Callable
import pandas as pd

from django.conf import settings
from django_datajsonar.models import Field, Distribution

from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask
from series_tiempo_ar_api.apps.management import meta_keys


logger = logging.Logger(__name__)


class CsvDumpWriter:
    """Escribe dumps de .csv de *datos*, iterando sobre las distribuciones de los fields pasados,
    y escribiendo un row por cada valor individual (par índice de tiempo - observación) de cada serie.
    El formato de cada row es especificado a través del callable rows.
    """

    def __init__(self, task: GenerateDumpTask, fields_data: dict, rows: Callable):
        self.task = task
        self.fields_data = fields_data
        # Funcion generadora de rows, especifica la estructura de la fila
        # a partir de argumentos pasados desde un pandas.apply
        self.rows = rows

    def write(self, filepath, header):
        fields = Field.objects.filter(
            enhanced_meta__key=meta_keys.AVAILABLE,
            identifier__in=self.fields_data.keys(),
        )

        distribution_ids = fields.values_list('distribution', flat=True)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

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

            periodicity = meta_keys.get(distribution, meta_keys.PERIODICITY)
            df.apply(self.write_serie, args=(periodicity, fields, writer))
        except Exception as e:
            msg = f'Error en la distribución {distribution.identifier}: {e.__class__}: {e}'
            GenerateDumpTask.info(self.task, msg)
            logger.error(msg)

    def write_serie(self, serie: pd.Series, periodicity: str, fields: dict, writer: csv.writer):
        field_id = fields[serie.name]

        # Filtrado de NaN
        serie = serie[serie.first_valid_index():serie.last_valid_index()]

        df = serie.reset_index().apply(self.rows,
                                       axis=1,
                                       args=(self.fields_data, field_id, periodicity))

        serie = pd.Series(df.values, index=serie.index)
        for row in serie:
            writer.writerow(row)
