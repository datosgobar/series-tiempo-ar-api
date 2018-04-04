#! coding: utf-8

CATALOG_NEW = 'catalogos_nuevos_cant'
CATALOG_UPDATED = 'catalogos_actualizados_cant'
CATALOG_TOTAL = 'catalogos_cant'

CATALOG_NOT_UPDATED = 'catalogos_no_actualizados_cant'

DATASET_NEW = 'datasets_nuevos_cant'
DATASET_UPDATED = 'datasets_actualizados_cant'
DATASET_TOTAL = 'datasets_cant'

DATASET_NOT_UPDATED = 'datasets_no_actualizados_cant'
DATASET_INDEXABLE = 'dataset_indexables_cant'
DATASET_NOT_INDEXABLE = 'datasets_no_indexables_cant'
DATASET_ERROR = 'datasets_error_cant'

DISTRIBUTION_NEW = 'distribuciones_nuevas_cant'
DISTRIBUTION_UPDATED = 'distribuciones_actualizadas_cant'
DISTRIBUTION_TOTAL = 'distribuciones_cant'

DISTRIBUTION_NOT_UPDATED = 'distribuciones_no_actualizadas_cant'
DISTRIBUTION_INDEXABLE = 'distribuciones_indexables_cant'
DISTRIBUTION_NOT_INDEXABLE = 'distribuciones_no_indexables_cant'
DISTRIBUTION_ERROR = 'distribuciones_error_cant'

FIELD_NEW = 'series_nuevas_cant'
FIELD_UPDATED = 'series_actualizadas_cant'
FIELD_TOTAL = 'field_cant'

FIELD_NOT_UPDATED = 'series_no_actualizadas_cant'
FIELD_INDEXABLE = 'series_indexables_cant'
FIELD_NOT_INDEXABLE = 'series_no_indexables_cant'
FIELD_ERROR = 'series_error_cant'

TYPE_CHOICES = (
    (CATALOG_NEW, 'Catálogos nuevos'),
    (CATALOG_TOTAL, 'Catálogos totales'),
    (CATALOG_UPDATED, 'Catálogos actualizados'),
    (CATALOG_NOT_UPDATED, 'Catálogos no actualizados'),
    (DATASET_NEW, 'Datasets nuevos'),
    (DATASET_TOTAL, 'Datasets totales'),
    (DATASET_UPDATED, 'Datasets actualizados'),
    (DATASET_NOT_UPDATED, 'Datasets no actualizados'),
    (DATASET_INDEXABLE, 'Datasets indexables'),
    (DATASET_NOT_INDEXABLE, 'Datasets no indexables'),
    (DATASET_ERROR, 'Datasets con errores'),
    (DISTRIBUTION_NEW, 'Distribuciones nuevas'),
    (DISTRIBUTION_TOTAL, 'Distribuciones totales'),
    (DISTRIBUTION_UPDATED, 'Distribuciones actualizadas'),
    (DISTRIBUTION_NOT_UPDATED, 'Distribuciones no actualizadas'),
    (DISTRIBUTION_INDEXABLE, 'Distribuciones indexables'),
    (DISTRIBUTION_NOT_INDEXABLE, 'Distribuciones no indexables'),
    (DISTRIBUTION_ERROR, 'Distribuciones con error'),
    (FIELD_NEW, 'Series nuevas'),
    (FIELD_TOTAL, 'Series totales'),
    (FIELD_UPDATED, 'Series actualizadas'),
    (FIELD_NOT_UPDATED, 'Series no actualizadas'),
    (FIELD_INDEXABLE, 'Series indexables'),
    (FIELD_NOT_INDEXABLE, 'Series no indexables'),
    (FIELD_ERROR, 'Series con error'),
)