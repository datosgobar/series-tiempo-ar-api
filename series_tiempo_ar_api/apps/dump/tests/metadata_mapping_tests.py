#! coding: utf-8
"""Tests de mapeo de columnas del dump de metadatos (CSV y SQLite).

Cada columna recibe un valor distinto, de modo que si un generador lee o
escribe una columna desde otra (por ejemplo, título del dataset desde el
tema, o consultas de 30 días desde las de 90), el test falla.

No necesitan base de datos, Elasticsearch ni archivos: prueban directamente
`MetadataCsvGenerator.generate_row` y `SQLGenerator.generate_series_rows`.
"""
from types import SimpleNamespace
from unittest import TestCase

from series_tiempo_ar_api.apps.dump.generator import constants
from series_tiempo_ar_api.apps.dump.generator.metadata import MetadataCsvGenerator
from series_tiempo_ar_api.apps.dump.generator.sql.generator import SQLGenerator
from series_tiempo_ar_api.apps.management import meta_keys

TEXT_COLUMNS = [
    constants.SERIES_TITLE,
    constants.SERIES_UNITS,
    constants.SERIES_DESCRIPTION,
    constants.DISTRIBUTION_TITLE,
    constants.DISTRIBUTION_DESCRIPTION,
    constants.DISTRIBUTION_DOWNLOAD_URL,
    constants.DATASET_PUBLISHER,
    constants.DATASET_SOURCE,
    constants.DATASET_TITLE,
    constants.DATASET_DESCRIPTION,
    constants.DATASET_THEME,
]

# Valores distintos y consistentes (30 <= 90 <= 180 <= total).
HITS = {
    constants.HITS_30_DAYS: 30,
    constants.HITS_90_DAYS: 90,
    constants.HITS_180_DAYS: 180,
    constants.HITS_TOTAL: 1000,
}


def build_field_values():
    """Arma el dict de un field tal como lo construye DumpGenerator.init_data."""
    values = {column: 'valor de {}'.format(column) for column in TEXT_COLUMNS}
    values.update({
        'dataset': SimpleNamespace(identifier='dataset-id',
                                   catalog=SimpleNamespace(identifier='catalogo-id')),
        'distribution': SimpleNamespace(identifier='distribucion-id'),
        'serie': SimpleNamespace(present=True),
        meta_keys.PERIODICITY: 'R/P1M',
        'metadata': {
            meta_keys.INDEX_START: '2010-01-01',
            meta_keys.INDEX_END: '2019-06-01',
            meta_keys.INDEX_SIZE: '114',
            meta_keys.DAYS_SINCE_LAST_UPDATE: '18',
            meta_keys.IS_UPDATED: 'True',
            meta_keys.LAST_VALUE: '12.5',
            meta_keys.SECOND_TO_LAST_VALUE: '10.0',
            meta_keys.LAST_PCT_CHANGE: '0.25',
            meta_keys.HITS_30_DAYS: HITS[constants.HITS_30_DAYS],
            meta_keys.HITS_90_DAYS: HITS[constants.HITS_90_DAYS],
            meta_keys.HITS_180_DAYS: HITS[constants.HITS_180_DAYS],
            meta_keys.HITS_TOTAL: HITS[constants.HITS_TOTAL],
        },
    })
    return values


def csv_row(values):
    generator = MetadataCsvGenerator(task=None, fields={}, catalog=None)
    return generator.generate_row('serie-id', values)


def sql_row(csv_dict):
    """Pasa una fila del CSV (como strings, en orden METADATA_ROWS) por el generador SQL."""
    reader = [[str(csv_dict[column]) for column in constants.METADATA_ROWS]]
    generator = SQLGenerator.__new__(SQLGenerator)  # evita __init__, que consulta la DB
    rows = list(generator.generate_series_rows(reader))
    assert len(rows) == 1
    return rows[0]


class MetadataCsvMappingTests(TestCase):

    def setUp(self):
        self.values = build_field_values()
        self.row = csv_row(self.values)

    def test_row_has_every_metadata_column(self):
        self.assertEqual(set(self.row), set(constants.METADATA_ROWS))

    def test_text_columns_come_from_their_own_field(self):
        for column in TEXT_COLUMNS:
            with self.subTest(column=column):
                self.assertEqual(self.row[column], self.values[column])

    def test_hits_columns_come_from_their_own_field(self):
        for column, expected in HITS.items():
            with self.subTest(column=column):
                self.assertEqual(self.row[column], expected)


class MetadataSqlMappingTests(TestCase):

    def setUp(self):
        # Fila de CSV con un valor distinto por columna, independiente del generador CSV.
        self.csv_dict = csv_row(build_field_values())
        self.csv_dict.update({column: 'valor de {}'.format(column) for column in TEXT_COLUMNS})
        self.csv_dict.update(HITS)
        self.metadatos = sql_row(self.csv_dict)

    def test_text_columns_come_from_their_own_csv_column(self):
        for column in TEXT_COLUMNS:
            with self.subTest(column=column):
                self.assertEqual(getattr(self.metadatos, column), self.csv_dict[column])

    def test_hits_columns_come_from_their_own_csv_column(self):
        for column, expected in HITS.items():
            with self.subTest(column=column):
                self.assertEqual(str(getattr(self.metadatos, column)), str(expected))

    def test_hits_are_ordered(self):
        m = self.metadatos
        self.assertLessEqual(int(m.consultas_30_dias), int(m.consultas_90_dias))
        self.assertLessEqual(int(m.consultas_90_dias), int(m.consultas_180_dias))
        self.assertLessEqual(int(m.consultas_180_dias), int(m.consultas_total))


class MetadataRoundTripTests(TestCase):
    """Field -> CSV -> SQLite: lo que entra por un campo sale por la misma columna."""

    def test_text_and_hits_survive_csv_and_sql(self):
        values = build_field_values()
        metadatos = sql_row(csv_row(values))

        for column in TEXT_COLUMNS:
            with self.subTest(column=column):
                self.assertEqual(getattr(metadatos, column), values[column])

        for column, expected in HITS.items():
            with self.subTest(column=column):
                self.assertEqual(str(getattr(metadatos, column)), str(expected))
