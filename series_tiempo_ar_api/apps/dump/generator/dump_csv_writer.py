import logging
import csv
import os
from typing import Callable
import pandas as pd

from django_datajsonar.models import Field, Distribution

from series_tiempo_ar_api.apps.dump.models import GenerateDumpTask
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.utils.distribution_csv_reader import DistributionCsvReader

logger = logging.Logger(__name__)


class CsvDumpWriter:
    """Escribe dumps de .csv de *datos*, iterando sobre las distribuciones de los fields pasados,
    y escribiendo un row por cada valor individual (par índice de tiempo - observación) de cada serie.
    El formato de cada row es especificado a través del callable rows.
    """

    def __init__(self, task: GenerateDumpTask, fields_data: dict, rows: Callable, tag: str):
        self.task = task
        self.fields_data = fields_data
        self.tag = tag
        # Funcion generadora de rows, especifica la estructura de la fila
        # a partir de argumentos pasados desde un pandas.apply
        self.rows = rows

    def write(self, filepath, header):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for distribution in self.get_distributions_sorted_by_identifier():
                self.write_distribution(distribution, writer)

    def get_distributions_sorted_by_identifier(self):
        fields = Field.objects.filter(
            identifier__in=self.fields_data.keys(),
        )
        distribution_ids = fields.values_list('distribution', flat=True)

        return Distribution.objects\
            .filter(id__in=distribution_ids)\
            .order_by('dataset__catalog__identifier', 'dataset__identifier', 'identifier')

    def write_distribution(self, distribution: Distribution, writer: csv.writer):
        # noinspection PyBroadException
        try:
            fields = distribution.field_set.all()
            fields = {field.title: field.identifier for field in fields}
            periodicity = meta_keys.get(distribution, meta_keys.PERIODICITY)
            index_col = DistributionRepository(distribution).get_time_index_series().title
            df = DistributionCsvReader(distribution, index_col).read()
            df.apply(self.write_serie, args=(periodicity, fields, writer))
        except Exception as e:
            msg = f'[{self.tag} Error en la distribución {distribution.identifier}: {e.__class__}: {e}'
            GenerateDumpTask.info(self.task, msg)
            logger.warning(msg)

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
