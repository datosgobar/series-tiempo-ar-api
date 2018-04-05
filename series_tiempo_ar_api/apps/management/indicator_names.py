#! coding: utf-8

CATALOG_NEW = 'catalogos_nuevos_cant'
CATALOG_UPDATED = 'catalogos_actualizados_cant'
CATALOG_NOT_UPDATED = 'catalogos_no_actualizados_cant'
CATALOG_TOTAL = 'catalogos_cant'
CATALOG_ERROR = 'catalogos_error_cant'

DATASET_UPDATED = 'datasets_actualizados_cant'
DATASET_NOT_UPDATED = 'datasets_no_actualizados_cant'
DATASET_INDEXABLE_DISCONTINUED = 'datasets_indexables_discontinuados_cant'
DATASET_INDEXABLE = 'datasets_indexables_cant'  # Suma de los tres anteriores
DATASET_ERROR = 'datasets_error_cant'
DATASET_NEW = 'datasets_nuevos_cant'
DATASET_NOT_INDEXABLE_PREVIOUS = 'datasets_no_indexables_anteriores_cant'
DATASET_NOT_INDEXABLE_DISCONTINUED = 'datasets_no_indexables_discontinuados_cant'
DATASET_NOT_INDEXABLE = 'datasets_no_indexables_cant'  # Suma de los tres anteriores
DATASET_AVAILABLE = 'datasets_disponibles_cant'
DATASET_TOTAL = 'datasets_cant'

DISTRIBUTION_UPDATED = 'distribuciones_actualizadas_cant'
DISTRIBUTION_NOT_UPDATED = 'distribuciones_no_actualizadas_cant'
DISTRIBUTION_INDEXABLE_DISCONTINUED = 'distribuciones_indexables_discontinuadas_cant'
DISTRIBUTION_INDEXABLE = 'distribuciones_indexables_cant'
DISTRIBUTION_ERROR = 'distribuciones_error_cant'
DISTRIBUTION_NEW = 'distribuciones_nuevas_cant'
DISTRIBUTION_NOT_INDEXABLE_PREVIOUS = 'distribuciones_no_indexables_anteriores_cant'
DISTRIBUTION_NOT_INDEXABLE_DISCONTINUED = 'distribuciones_no_indexables_discontinuadas_cant'
DISTRIBUTION_NOT_INDEXABLE = 'distribuciones_no_indexables_cant'
DISTRIBUTION_AVAILABLE = 'distribuciones_disponibles_cant'
DISTRIBUTION_TOTAL = 'distribuciones_cant'

FIELD_UPDATED = 'series_actualizadas_cant'
FIELD_NOT_UPDATED = 'series_no_actualizadas_cant'
FIELD_INDEXABLE_DISCONTINUED = 'series_indexables_discontinuadas_cant'
FIELD_INDEXABLE = 'series_indexables_cant'
FIELD_ERROR = 'series_error_cant'
FIELD_NEW = 'series_nuevas_cant'
FIELD_NOT_INDEXABLE_PREVIOUS = 'series_no_indexables_anteriores_cant'
FIELD_NOT_INDEXABLE_DISCONTINUED = 'series_no_indexables_discontinuadas_cant'
FIELD_NOT_INDEXABLE = 'series_no_indexables_cant'
FIELD_AVAILABLE = 'series_disponibles_cant'
FIELD_TOTAL = 'field_cant'

TYPE_CHOICES = (
    (CATALOG_NEW, 'Catálogos nuevos'),
    (CATALOG_UPDATED, 'Catálogos actualizados'),
    (CATALOG_NOT_UPDATED, 'Catálogos no actualizados'),
    (CATALOG_TOTAL, 'Catálogos totales'),
    (CATALOG_ERROR, 'Catálogos con error'),
    (DATASET_UPDATED, 'Datasets actualizados'),
    (DATASET_NOT_UPDATED, 'Datasets no actualizados'),
    (DATASET_INDEXABLE_DISCONTINUED, 'Datasets indexables (discontinuados)'),
    (DATASET_INDEXABLE, 'Datasets indexables'),
    (DATASET_ERROR, 'Datasets con errores'),
    (DATASET_NEW, 'Datasets no indexables (nuevos)'),
    (DATASET_NOT_INDEXABLE_PREVIOUS, 'Datasets no indexables (anteriores)'),
    (DATASET_NOT_INDEXABLE_DISCONTINUED, 'Datasets no indexables (discontinuados)'),
    (DATASET_NOT_INDEXABLE, 'Datasets no indexables (total)'),
    (DATASET_AVAILABLE, 'Datasets disponibles'),
    (DATASET_TOTAL, 'Datasets totales'),
    (DISTRIBUTION_UPDATED, 'Distribuciones actualizadas'),
    (DISTRIBUTION_NOT_UPDATED, 'Distribuciones no actualizadas'),
    (DISTRIBUTION_INDEXABLE_DISCONTINUED, 'Distribuciones indexables (discontinuadas)'),
    (DISTRIBUTION_INDEXABLE, 'Distribuciones indexables'),
    (DISTRIBUTION_ERROR, 'Distribuciones con error'),
    (DISTRIBUTION_NEW, 'Distribuciones no indexables (nuevas)'),
    (DISTRIBUTION_NOT_INDEXABLE_PREVIOUS, 'Distribuciones no indexables (anteriores)'),
    (DISTRIBUTION_NOT_INDEXABLE_DISCONTINUED, 'Distribuciones no indexables (discontinuadas)'),
    (DISTRIBUTION_NOT_INDEXABLE, 'Distribuciones no indexables'),
    (DISTRIBUTION_AVAILABLE, 'Distribuciones disponibles'),
    (DISTRIBUTION_TOTAL, 'Distribuciones totales'),
    (FIELD_UPDATED, 'Series actualizadas'),
    (FIELD_NOT_UPDATED, 'Series no actualizadas'),
    (FIELD_INDEXABLE_DISCONTINUED, 'Series indexables (discontinuadas)'),
    (FIELD_INDEXABLE, 'Series indexables'),
    (FIELD_ERROR, 'Series con error'),
    (FIELD_NEW, 'Series no indexables (nuevas)'),
    (FIELD_NOT_INDEXABLE_PREVIOUS, 'Series no indexables (anteriores)'),
    (FIELD_NOT_INDEXABLE_DISCONTINUED, 'Series no indexables (discontinuadas)'),
    (FIELD_NOT_INDEXABLE, 'Series no indexables'),
    (FIELD_AVAILABLE, 'Series disponibles'),
    (FIELD_TOTAL, 'Series totales'),
)
