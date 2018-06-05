#! coding: utf-8
import os
from django.conf import settings


DUMP_DIR = os.path.join(settings.MEDIA_ROOT, 'dump')

# Filenames de los archivos a generar y ofrecer
FULL_CSV_ZIPPED = 'series-tiempo-csv.zip'
VALUES_CSV = 'series-tiempo-valores.csv'
METADATA_CSV = 'series-tiempo-metadata.csv'
SOURCES_CSV = 'series-tiempo-fuentes.csv'

# Archivo sin zippear, no es descargable
FULL_CSV = 'series-tiempo.csv'

# Archivos a servir por endpoint
FILES = [
    FULL_CSV_ZIPPED,
    VALUES_CSV,
    METADATA_CSV,
    SOURCES_CSV
]


VALUES_HEADER = [
    'catalogo_id',
    'dataset_id',
    'distribucion_id',
    'serie_id',
    'indice_tiempo',
    'valor',
    'indice_tiempo_frecuencia'
]

FULL_CSV_HEADER = [
    'catalogo_id',
    'dataset_id',
    'distribucion_id',
    'serie_id',
    'indice_tiempo',
    'indice_tiempo_frecuencia',
    'valor',
    'serie_titulo',
    'serie_unidades',
    'serie_descripcion',
    'distribucion_descripcion',
    'dataset_tema',
    'dataset_responsable',
    'dataset_fuente',
    'dataset_titulo',
]


DUMPS_NOT_GENERATED = "Dumps no generados"
DUMP_ERROR = "Error en la lectura del archivo pedido"
OLD_DUMP_FILES_AMOUNT = 3  # Cantidad de dumps a retener en disco (incluyendo el más reciente)
