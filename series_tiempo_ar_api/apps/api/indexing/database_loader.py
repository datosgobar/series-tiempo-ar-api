#! coding: utf-8
import json
import logging
import hashlib
from tempfile import NamedTemporaryFile

import requests
from django.conf import settings
from django.core.files import File
from django.db import IntegrityError
from django.db.models.query_utils import Q
from django.utils import timezone
from pydatajson import DataJson
from pydatajson.search import get_dataset

from series_tiempo_ar_api.apps.api.models import \
    Dataset, Catalog, Distribution, Field

from series_tiempo_ar_api.apps.api.indexing import strings
from series_tiempo_ar_api.apps.api.indexing import constants


logger = logging.getLogger(__name__)


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self, read_local=False, default_whitelist=False):
        self.distribution_models = []
        self.dataset_cache = {}
        self.catalog_model = None
        self.read_local = read_local
        self.catalog_id = None
        self.stats = {}
        self.default_whitelist = default_whitelist

    def run(self, catalog, catalog_id, distributions):
        """Guarda las distribuciones de la lista 'distributions',
        asociadas al catálogo 'catalog, en la base de datos, junto con
        todos los metadatos de distinto nivel (catalog, dataset)

        Args:
            catalog (DataJson)
            catalog_id (str): Identificador único del catalogo a guardar
            distributions (list)
        """
        self.catalog_id = catalog_id
        logger.info(strings.DB_LOAD_START)
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

                if distribution_model:
                    self._save_fields(distribution_model, fields)

        self._update_present_datasets(catalog_id)
        logger.info(strings.DB_LOAD_END)

    def _catalog_model(self, catalog):
        """Crea o actualiza el catalog model con el título pedido a partir
        de el diccionario de metadatos de un catálogo
        """
        catalog = catalog.copy()
        # Borro el dataset, de existir. Solo guardo metadatos
        catalog.pop(constants.DATASET, None)
        catalog_model, created = Catalog.objects.get_or_create(identifier=self.catalog_id)

        catalog = self._remove_blacklisted_fields(
            catalog,
            settings.CATALOG_BLACKLIST
        )
        catalog_model.metadata = json.dumps(catalog)
        catalog_model.title = catalog.get(constants.FIELD_TITLE)
        catalog_model.save()
        self.stats['catalogs'] = self.stats.get('catalogs', 0) + created
        self.stats['total_catalogs'] = self.stats.get('total_catalogs', 0) + 1

        return catalog_model

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
        dataset_model, created = Dataset.objects.get_or_create(
            identifier=identifier,
            catalog=self.catalog_model,
        )
        if created:
            dataset_model.indexable = self.default_whitelist

        dataset = self._remove_blacklisted_fields(
            dataset,
            settings.DATASET_BLACKLIST
        )
        dataset_model.metadata = json.dumps(dataset)
        dataset_model.save()

        self.dataset_cache[dataset[constants.IDENTIFIER]] = dataset_model

        self.stats['datasets'] = self.stats.get('datasets', 0) + created
        self.stats['total_datasets'] = self.stats.get('total_datasets', 0) + 1
        return dataset_model

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
        if not dataset_model.indexable:
            return None

        distribution_model, created = Distribution.objects.get_or_create(
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

        self.stats['distributions'] = self.stats.get('distributions', 0) + created
        self.stats['total_distributions'] = self.stats.get('total_distributions', 0) + 1
        return distribution_model

    def _read_file(self, file_url, distribution_model):
        """Descarga y lee el archivo de la distribución. Por razones
        de performance, NO hace un save() a la base de datos.

        Args:
            file_url (str)
            distribution_model (Distribution)
        """
        data_hash = ''
        if self.read_local:  # Usado en debug y testing
            with open(file_url) as f:
                data_hash = f.read()

            distribution_model.data_file = File(open(file_url))

        else:
            request = requests.get(file_url, stream=True)

            if request.status_code != 200:
                return False

            lf = NamedTemporaryFile()

            lf.write(request.content)

            if distribution_model.data_file:
                distribution_model.data_file.delete()

            distribution_model.data_file = File(lf)

        if distribution_model.data_hash != data_hash:
            distribution_model.data_hash = data_hash
            distribution_model.last_updated = timezone.now()
            distribution_model.indexable = True
        else:  # No cambió respecto a la corrida anterior
            distribution_model.indexable = False

    def _save_fields(self, distribution_model, fields):
        for field in fields:
            if field.get(constants.SPECIAL_TYPE) == constants.TIME_INDEX:
                continue

            series_id = field.get(constants.FIELD_ID)
            title = field.get(constants.FIELD_TITLE)
            try:
                field_model, created = Field.objects.get_or_create(
                    series_id=series_id,
                    title=title,
                    distribution=distribution_model
                )
            except IntegrityError:  # Series ID ya existía
                logger.warn(strings.DB_SERIES_ID_REPEATED, series_id, self.catalog_id)
                continue
            field = self._remove_blacklisted_fields(
                field,
                settings.FIELD_BLACKLIST
            )
            field_model.description = field[constants.FIELD_DESCRIPTION]
            field_model.metadata = json.dumps(field)

            # Borra modelos viejos en caso de que haya habido un cambio de series id
            distribution_model.field_set.filter(title=title).delete()
            field_model.save()

            self.stats['fields'] = self.stats.get('fields', 0) + created
            self.stats['total_fields'] = self.stats.get('total_fields', 0) + 1

    @staticmethod
    def _remove_blacklisted_fields(metadata, blacklist):
        """Borra los campos listados en 'blacklist' de el diccionario
        'metadata'
        """

        for field in blacklist:
            metadata.pop(field, None)
        return metadata

    def _update_present_datasets(self, catalog_id):
        """Actualiza la lista de datasets marcando los datasets encontrados como presentes"""

        present_ids = self.dataset_cache.keys()
        datasets = Dataset.objects.filter(~Q(identifier__in=present_ids),
                                          Q(catalog__identifier=catalog_id))
        datasets.update(present=False)

    def get_stats(self):
        return self.stats
