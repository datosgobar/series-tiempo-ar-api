import json
import csv

import pandas as pd
from django.conf import settings

from django_datajsonar.models import Field, Distribution

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.dump.models import CSVDumpTask


class DumpGenerator:

    def __init__(self):
        self.fields = {}
        self.themes = {}

        self.task = CSVDumpTask.objects.create()

        self.init_data()

    def init_data(self):
        """Inicializa en un diccionario con IDs de series como clave los valores a escribir en cada
        uno de los CSV.
        """
        fields = Field.objects.filter(
            enhanced_meta__key=meta_keys.AVAILABLE,
        ).prefetch_related(
            'distribution',
            'distribution__dataset',
            'distribution__dataset__catalog',
            'enhanced_meta',
        )

        for field in fields:
            meta = json.loads(field.metadata)
            dist_meta = json.loads(field.distribution.metadata)
            dataset_meta = json.loads(field.distribution.dataset.metadata)
            themes = field.distribution.dataset.themes
            theme_labels = get_theme_labels(json.loads(themes)) if themes else ''

            self.fields[field.identifier] = {
                'dataset': field.distribution.dataset,
                'distribution': field.distribution,
                'serie_titulo': field.title,
                'serie_unidades': meta.get('units'),
                'serie_descripcion': meta.get('description'),
                'distribucion_descripcion': dist_meta.get('description'),
                'dataset_tema': theme_labels,
                'dataset_responsable': dataset_meta.get('publisher', {}).get('name'),
                'dataset_titulo': field.distribution.dataset.title,
                'dataset_fuente': dataset_meta.get('source'),
            }

    def write_distribution(self, distribution: Distribution):
        df = pd.read_csv(distribution.data_file.file,
                         index_col=settings.INDEX_COLUMN,
                         parse_dates=[settings.INDEX_COLUMN])
        fields = distribution.field_set.all()
        fields = {field.title: field.identifier for field in fields}

        df.apply(self.write_serie, args=(distribution, fields,))

    def write_serie(self, serie: pd.Series, distribution: Distribution, fields: dict):
        field_id = fields[serie.name]
        with open('data.csv', mode='a') as f:
            writer = csv.writer(f)
            df = serie.reset_index().apply(self.full_csv_row,
                                           axis=1,
                                           args=(field_id, meta_keys.get(distribution, meta_keys.PERIODICITY)))

            serie = pd.Series(df.values, index=serie.index)
            for row in serie:
                writer.writerow(row)

    def generate(self):
        distribution_ids = Field.objects.filter(
            enhanced_meta__key=meta_keys.AVAILABLE,
        ).values_list('distribution', flat=True)

        with open('data.csv', mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(constants.FULL_CSV_HEADER)

        for distribution in Distribution.objects.filter(id__in=distribution_ids).order_by('identifier'):
            self.write_distribution(distribution)

    def full_csv_row(self, value, field, periodicity):
        dataset = self.fields[field]['dataset']
        return (
            dataset.catalog.identifier,
            dataset.identifier,
            self.fields[field]['distribution'].identifier,
            field,
            value[0],  # Index
            periodicity,
            value[1],  # Value
            self.fields[field]['serie_titulo'],
            self.fields[field]['serie_unidades'],
            self.fields[field]['serie_descripcion'],
            self.fields[field]['distribucion_descripcion'],
            self.fields[field]['dataset_tema'],
            self.fields[field]['dataset_responsable'],
            self.fields[field]['dataset_fuente'],
            self.fields[field]['dataset_titulo'],
        )


def get_theme_labels(themes: list):
    """Devuelve un string con los labels de themes del dataset separados por comas"""
    labels = []
    for theme in themes:
        labels.append(theme['label'])

    return ','.join(labels)
