#! coding: utf-8
import hashlib
import json
from tempfile import NamedTemporaryFile

import requests
from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import Indicator, ReadDataJsonTask
from . import constants
from series_tiempo_ar_api.apps.api.models import \
    Dataset, Catalog, Distribution, Field


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self, task, read_local=False, default_whitelist=False):
        self.task = task
        self.catalog_model = None
        self.catalog_id = None
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
        self.catalog_id = catalog_id
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

        if distribution_model.indexable:
            self._save_fields(distribution_model, fields)

        for _ in fields[1:]:  # El primero es el índice de tiempo, no considerado
            self.increment_indicator(Indicator.FIELD_TOTAL)

        return distribution_model if distribution_model.indexable else None

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
        catalog_meta = json.dumps(catalog)

        catalog_model.title = catalog.get(constants.FIELD_TITLE)
        if created:
            self.increment_indicator(Indicator.CATALOG_NEW)
        elif catalog_model.metadata != catalog_meta:
            catalog_model = self.set_as_updated(catalog_model)

        catalog_model.metadata = catalog_meta
        catalog_model.save()

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
        dataset_meta = json.dumps(dataset)
        dataset_model.present = True

        if created:
            self.increment_indicator(Indicator.DATASET_NEW)
        elif dataset_meta != dataset_model.metadata:
            dataset_model = self.set_as_updated(dataset_model)

        dataset_model.metadata = dataset_meta
        dataset_model.save()

        return dataset_model

    def _distribution_model(self, distribution, dataset_model, periodicity):
        """Crea o actualiza el modelo de la distribución a partir de
        un diccionario que lo representa
        """
        distribution = distribution.copy()
        # Borro los fields, de existir. Sólo guardo metadatos
        fields = distribution.pop(constants.FIELD, None)
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
        distribution_meta = json.dumps(distribution)
        distribution_model.download_url = url
        distribution_model.periodicity = periodicity
        updated = False
        if dataset_model.indexable:
            updated = self._read_file(url, distribution_model)

        if updated:
            distribution_model.indexable = True

        if created:
            self.increment_indicator(Indicator.DISTRIBUTION_NEW)
            # Cuenta todos sus fields como nuevos
            # Se hace acá porque se tienen que contar pero no instanciar su modelo,
            # No se corre el método _save_fields sobre distribuciones recién creadas
            for _ in fields[1:]:
                self.increment_indicator(Indicator.FIELD_NEW)

        elif updated or distribution_meta != distribution_model.metadata:
            self.increment_indicator(Indicator.DISTRIBUTION_UPDATED)
            if not self.read_updated(dataset_model):
                self.set_as_updated(dataset_model)
                self.increment_indicator(Indicator.DATASET_UPDATED)

            if not self.read_updated(self.catalog_model):
                self.set_as_updated(self.catalog_model)
                self.increment_indicator(Indicator.CATALOG_UPDATED)

            for _ in fields[1:]:
                self.increment_indicator(Indicator.FIELD_UPDATED)
        self.increment_indicator(Indicator.DISTRIBUTION_TOTAL)

        distribution_model.metadata = distribution_meta
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
            return True
        else:  # No cambió respecto a la corrida anterior
            distribution_model.indexable = False
            return False

    def _save_fields(self, distribution_model, fields):
        fields = [field for field in fields if field.get(constants.SPECIAL_TYPE) != constants.TIME_INDEX]
        for field in fields:

            series_id = field.get(constants.FIELD_ID)

            # No vale get_or_create, distribution_model puede haber diferido desde la última ejecución
            field_model = Field.objects.filter(series_id=series_id)
            if not field_model:
                field_model = Field(series_id=series_id)
                created = True
            else:
                field_model = field_model[0]
                created = False

                old_catalog_id = field_model.distribution.dataset.catalog.identifier
                if old_catalog_id != self.catalog_id:
                    raise FieldRepetitionError(u"Serie {} repetida en catálogos {} y {}".format(
                        series_id, old_catalog_id, self.catalog_id
                    ))

            title = field.get(constants.FIELD_TITLE)
            field_model.title = title
            field_model.distribution = distribution_model
            field = self._remove_blacklisted_fields(
                field,
                settings.FIELD_BLACKLIST
            )
            field_model.description = field[constants.FIELD_DESCRIPTION]

            field_meta = json.dumps(field)
            # Borra modelos viejos en caso de que haya habido un cambio de series id
            # Necesario para poder mantener una relación 1:1 entre modelos de la DB y columnas del CSV
            distribution_model.field_set.filter(title=title).delete()

            # Por ahora todos los field son considerados como updated si su distribución lo es
            field_model = self.set_as_updated(field_model)

            field_model.metadata = field_meta
            field_model.save()

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

    def increment_indicator(self, indicator_type):
        ReadDataJsonTask.increment_indicator(self.task, self.catalog_id, indicator_type)

    # Lectura / Escritura del campo updated protegiendose de race conditions

    @staticmethod
    def set_as_updated(model):
        model.save()
        with transaction.atomic():
            model = model.__class__.objects.select_for_update().get(id=model.id)
            model.updated = True
            model.save()
            return model

    @staticmethod
    def read_updated(model):
        with transaction.atomic():
            return model.__class__.objects.select_for_update().get(id=model.id).updated


class FieldRepetitionError(Exception):
    pass
