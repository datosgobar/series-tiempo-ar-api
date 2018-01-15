#! coding: utf-8
from __future__ import division

import json
import logging
import StringIO


from pydatajson import DataJson

from series_tiempo_ar_api.apps.api.indexing.database_loader import \
    DatabaseLoader
from series_tiempo_ar_api.apps.api.indexing.indexer import Indexer
from series_tiempo_ar_api.apps.api.indexing.scraping import get_scraper
from series_tiempo_ar_api.apps.api.indexing import strings
from series_tiempo_ar_api.apps.api.models import Dataset, Distribution


def get_string_logger(logger_name, level=logging.INFO, _format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"):
    """
    Gets you what you need to log to a string. Returns a pair of StringIO, logger variables.

    output, logger = get_string_logger('my_app_logger', level=logging.DEBUG)
    call_stuff_to_debug_with_logger(logger=logger)
    print output.getvalue()
    """
    _logger = logging.getLogger(logger_name)
    _logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(_format)
    _output = StringIO.StringIO()
    string_handler = logging.StreamHandler(_output)
    string_handler.setFormatter(formatter)
    string_handler.setLevel(level)
    _logger.addHandler(string_handler)

    return _output, _logger


output, logger = get_string_logger(__name__)


def index_catalog(catalog, catalog_id, read_local=False, task=None):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre el catálogo especificado

    Args:
        catalog (DataJson): DataJson del catálogo a parsear
        catalog_id (str): ID único del catálogo a parsear
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
        task (ReadDataJsonTask): Task a loggear acciones
    """
    logger.info(strings.PIPELINE_START, catalog_id)
    scraper = get_scraper(read_local)
    scraper.run(catalog)
    distributions = scraper.distributions

    loader = DatabaseLoader(read_local)
    loader.run(catalog, catalog_id, distributions)

    # Indexo todos los datasets whitelisteados, independientemente de cuales fueron
    # scrapeados / cargados
    datasets = Dataset.objects.filter(catalog__identifier=catalog_id,
                                      present=True,
                                      indexable=True)
    distribution_models = Distribution.objects.filter(dataset__in=datasets)
    Indexer().run(distribution_models)

    if task:
        stats = loader.get_stats()
        task_stats = json.loads(task.stats)
        task_stats[catalog_id] = stats
        task.stats = json.dumps(task_stats)

        task.logs = (task.logs + output.getvalue()) or '-'
        task.save()
