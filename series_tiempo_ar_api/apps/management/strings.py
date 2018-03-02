#! coding: utf-8

DATASET_STATUS = u"Dataset ({}, {}) status: {}"
FILE_READ_ERROR = u"Error en la lectura del archivo de entrada"

# Identificador para los crons de indexing
CRONTAB_COMMENT = u"API series tiempo: indexing de datos"

INDEXING_REPORT_TEMPLATE = \
    u"""
{name}:
    nuevos: {new},
    actualizados: {updated},
    totales: {total},
"""
