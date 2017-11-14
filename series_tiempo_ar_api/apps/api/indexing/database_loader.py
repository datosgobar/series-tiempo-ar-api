#! coding: utf-8
import json
import logging
from tempfile import NamedTemporaryFile

import requests
from django.conf import settings
from django.core.files import File
from pydatajson import DataJson
from pydatajson.search import get_dataset

from series_tiempo_ar_api.apps.api.models import \
    Dataset, Catalog, Distribution, Field

import constants
from .strings import DB_LOAD_START, DB_LOAD_END


logger = logging.Logger(__name__)
logger.addHandler(logging.StreamHandler())


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self, read_local=False):
        self.distribution_models = []
        self.dataset_cache = {}
        self.catalog_model = None
        self.read_local = read_local

    def run(self, catalog, distributions):
        """Guarda las distribuciones de la lista 'distributions',
        asociadas al catálogo 'catalog, en la base de datos, junto con
        todos los metadatos de distinto nivel (catalog, dataset)

        Args:
            catalog (DataJson)
            distributions (list)
        """
        logger.info(DB_LOAD_START)
        catalog = DataJson(catalog)
        self.catalog_model = self._catalog_model(catalog)
        for distribution in distributions:
            fields = distribution[constants.FIELD]
            time_distribution = False
            periodicity = None
            for field in fields:
                if field.get(constants.SPECIAL_TYPE) == constants.TIME_INDEX:
                    periodicity = field.get(constants.SPECIAL_TYPE_DETAIL)
                    time_distribution = True
                    break

            if time_distribution:
                distribution_model = self._distribution_model(catalog,
                                                              distribution,
                                                              periodicity)

                self._save_fields(distribution_model, fields)
        logger.info(DB_LOAD_END)

    def _dataset_model(self, dataset):
        """Crea o actualiza el modelo del dataset a partir de un
        diccionario que lo representa
        """
        if dataset[constants.IDENTIFIER] in self.dataset_cache:
            return self.dataset_cache[dataset[constants.IDENTIFIER]]

        dataset = dataset.copy()
        # Borro las distribuciones, de existir. Solo guardo metadatos
        dataset.pop(constants.DISTRIBUTION, None)
        identifier = dataset[constants.IDENTIFIER]
        dataset_model, _ = Dataset.objects.get_or_create(
            identifier=identifier,
            catalog=self.catalog_model
        )

        dataset = self._remove_blacklisted_fields(
            dataset,
            settings.DATASET_BLACKLIST
        )
        dataset_model.metadata = json.dumps(dataset)
        dataset_model.save()

        self.dataset_cache[dataset[constants.IDENTIFIER]] = dataset_model
        return dataset_model

    def _catalog_model(self, catalog):
        """Crea o actualiza el catalog model con el título pedido a partir
        de el diccionario de metadatos de un catálogo
        """
        catalog = catalog.copy()
        # Borro el dataset, de existir. Solo guardo metadatos
        catalog.pop(constants.DATASET, None)
        title = catalog.get(constants.FIELD_TITLE)
        catalog_model, _ = Catalog.objects.get_or_create(title=title)

        catalog = self._remove_blacklisted_fields(
            catalog,
            settings.CATALOG_BLACKLIST
        )
        catalog_model.metadata = json.dumps(catalog)
        catalog_model.save()
        return catalog_model

    def _distribution_model(self, catalog, distribution, periodicity):
        """Crea o actualiza el modelo de la distribución a partir de
        un diccionario que lo representa
        """
        distribution = distribution.copy()
        # Borro los fields, de existir. Sólo guardo metadatos
        distribution.pop(constants.FIELD, None)
        identifier = distribution[constants.IDENTIFIER]
        url = distribution.get(constants.DOWNLOAD_URL)
        dataset_identifier = distribution.get(constants.DATASET_IDENTIFIER)
        dataset = get_dataset(catalog, identifier=dataset_identifier)

        dataset.pop(constants.DISTRIBUTION, None)
        dataset_model = self._dataset_model(dataset)
        distribution_model, _ = Distribution.objects.get_or_create(
            identifier=identifier,
            dataset=dataset_model
        )
        distribution = self._remove_blacklisted_fields(
            distribution,
            settings.DISTRIBUTION_BLACKLIST
        )
        distribution_model.metadata = json.dumps(distribution)
        distribution_model.download_url = url
        distribution_model.periodicity = periodicity
        self._read_file(url, distribution_model)
        distribution_model.save()
        self.distribution_models.append(distribution_model)
        return distribution_model

    def _read_file(self, file_url, distribution_model):
        """Descarga y lee el archivo de la distribución. Por razones
        de performance, NO hace un save() a la base de datos.

        Args:
            file_url (str)
            distribution_model (Distribution)
        """
        if self.read_local:  # Usado en debug y testing
            distribution_model.data_file = File(open(file_url))
            return

        request = requests.get(file_url, stream=True)

        if request.status_code != 200:
            return False

        lf = NamedTemporaryFile()

        block_size = 1024 * 8
        for block in request.iter_content(block_size):
            lf.write(block)

        if distribution_model.data_file:
            distribution_model.data_file.delete()

        distribution_model.data_file = File(lf)

    def _save_fields(self, distribution_model, fields):
        for field in fields:
            if field.get(constants.SPECIAL_TYPE) == constants.TIME_INDEX:
                continue

            series_id = field.get(constants.FIELD_ID)
            title = field.get(constants.FIELD_TITLE)
            field_model, _ = Field.objects.get_or_create(
                series_id=series_id,
                title=title,
                distribution=distribution_model
            )
            field = self._remove_blacklisted_fields(
                field,
                settings.FIELD_BLACKLIST
            )
            field_model.metadata = json.dumps(field)
            field_model.save()

    @staticmethod
    def _remove_blacklisted_fields(metadata, blacklist):
        """Borra los campos listados en 'blacklist' de el diccionario
        'metadata'
        """

        for field in blacklist:
            metadata.pop(field, None)
        return metadata