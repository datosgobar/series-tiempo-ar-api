#! coding: utf-8
import hashlib
import json
from tempfile import NamedTemporaryFile

import requests
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from pydatajson import DataJson

from . import constants
from series_tiempo_ar_api.apps.api.models import \
    Dataset, Catalog, Distribution, Field


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self, read_local=False, default_whitelist=False):
        self.catalog_model = None
        self.stats = {}
        self.read_local = read_local
        self.default_whitelist = default_whitelist

    def run(self, distribution, catalog, catalog_id):
        """Guarda las distribuciones de la lista 'distributions',
        asociadas al catálogo 'catalog, en la base de datos, junto con
        todos los metadatos de distinto nivel (catalog, dataset)

        Args:
            distribution (dict)
            catalog (DataJson)
            catalog_id (str): Identificador único del catalogo a guardar
        Returns:
            Distribution: distribución creada, o None si falla
        """
        self.catalog_model = self._catalog_model(catalog, catalog_id)
        dataset = catalog.get_dataset(distribution[constants.DATASET_IDENTIFIER])
        dataset.pop(constants.DISTRIBUTION)
        dataset_model = self._dataset_model(dataset)
        fields = distribution[constants.FIELD]
        periodicity = None
        for field in fields:
            if field.get(constants.SPECIAL_TYPE) == constants.TIME_INDEX:
                periodicity = field.get(constants.SPECIAL_TYPE_DETAIL)
                break

        distribution_model = self._distribution_model(distribution, dataset_model, periodicity)

        if distribution_model:
            self._save_fields(distribution_model, fields)
            return distribution_model

    def _catalog_model(self, catalog, catalog_id):
        """Crea o actualiza el catalog model con el título pedido a partir
        de el diccionario de metadatos de un catálogo
        """
        catalog = catalog.copy()
        # Borro el dataset, de existir. Solo guardo metadatos
        catalog.pop(constants.DATASET, None)
        catalog_model, created = Catalog.objects.get_or_create(identifier=catalog_id)

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
        dataset_model.present = True
        dataset_model.save()

        self.stats['datasets'] = self.stats.get('datasets', 0) + created
        self.stats['total_datasets'] = self.stats.get('total_datasets', 0) + 1
        return dataset_model

    def _distribution_model(self, distribution, dataset_model, periodicity):
        """Crea o actualiza el modelo de la distribución a partir de
        un diccionario que lo representa
        """
        distribution = distribution.copy()
        # Borro los fields, de existir. Sólo guardo metadatos
        distribution.pop(constants.FIELD, None)
        identifier = distribution[constants.IDENTIFIER]
        url = distribution.get(constants.DOWNLOAD_URL)

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

        self.stats['distributions'] = self.stats.get('distributions', 0) + created
        self.stats['total_distributions'] = self.stats.get('total_distributions', 0) + 1
        distribution_model.save()
        return distribution_model

    def _read_file(self, file_url, distribution_model):
        """Descarga y lee el archivo de la distribución. Por razones
        de performance, NO hace un save() a la base de datos.
        Marca el modelo de distribución como 'indexable' si el archivo tiene datos
        distintos a los actuales. El chequeo de cambios se hace hasheando el archivo entero
        Args:
            file_url (str)
            distribution_model (Distribution)
        """
        if self.read_local:  # Usado en debug y testing
            with open(file_url) as f:
                data_hash = hashlib.sha512(f.read()).hexdigest()

            distribution_model.data_file = File(open(file_url))

        else:
            request = requests.get(file_url, stream=True)
            request.raise_for_status()  # Excepción si es inválido

            lf = NamedTemporaryFile()

            lf.write(request.content)

            if distribution_model.data_file:
                distribution_model.data_file.delete()

            distribution_model.data_file = File(lf)
            data_hash = hashlib.sha512(request.content).hexdigest()

        if distribution_model.data_hash != data_hash:
            distribution_model.data_hash = data_hash
            distribution_model.last_updated = timezone.now()
            distribution_model.indexable = True
        else:  # No cambió respecto a la corrida anterior
            distribution_model.indexable = False

    def _save_fields(self, distribution_model, fields):
        fields = [field for field in fields if field.get(constants.SPECIAL_TYPE) != constants.TIME_INDEX]
        for field in fields:

            series_id = field.get(constants.FIELD_ID)
            title = field.get(constants.FIELD_TITLE)
            field_model, created = Field.objects.get_or_create(
                series_id=series_id,
                title=title,
                distribution=distribution_model
            )

            field = self._remove_blacklisted_fields(
                field,
                settings.FIELD_BLACKLIST
            )
            field_model.description = field[constants.FIELD_DESCRIPTION]
            field_model.metadata = json.dumps(field)

            # Borra modelos viejos en caso de que haya habido un cambio de series id
            # Necesario para poder mantener una relación 1:1 entre modelos de la DB y columnas del CSV
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

    def get_stats(self):
        return self.stats
