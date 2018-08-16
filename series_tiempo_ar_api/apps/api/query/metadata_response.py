#! coding: utf-8
import json
from typing import Union

from django_datajsonar.models import Field, Catalog, Dataset, Distribution

from series_tiempo_ar_api.apps.api.query import constants


class MetadataResponse:
    datajson_entity = Union[Catalog, Dataset, Distribution, Field]

    def __init__(self, field: Field):
        self.field = field

    def get_simple_metadata(self):
        """Obtiene los campos de metadatos marcados como simples en
        la configuración de un modelo de una serie. La estructura
        final de metadatos respeta el formato de un data.json
        """

        # Idea: obtener todos los metadatos y descartar los que no queremos
        meta = self.get_full_metadata()

        catalog = meta['catalog']
        for meta_field in list(catalog):
            if meta_field not in constants.CATALOG_SIMPLE_META_FIELDS:
                catalog.pop(meta_field)

        dataset = meta['dataset']
        for meta_field in list(dataset):
            if meta_field not in constants.DATASET_SIMPLE_META_FIELDS:
                dataset.pop(meta_field)

        distribution = meta['distribution']
        for meta_field in list(distribution):
            if meta_field not in constants.DISTRIBUTION_SIMPLE_META_FIELDS:
                distribution.pop(meta_field)

        field = meta['field']
        for meta_field in list(field):
            if meta_field not in constants.FIELD_SIMPLE_META_FIELDS:
                field.pop(meta_field)

        return meta

    def get_full_metadata(self):
        distribution = self.field.distribution
        dataset = distribution.dataset
        catalog = dataset.catalog

        dataset_meta = self._get_full_metadata_for_model(dataset)
        self.replace_dataset_theme(dataset_meta)

        return {
            'catalog': self._get_full_metadata_for_model(catalog),
            'dataset': dataset_meta,
            'distribution': self._get_full_metadata_for_model(distribution),
            'field': self._get_full_metadata_for_model(self.field),
        }

    def _get_full_metadata_for_model(self, model: datajson_entity):
        metadata = {}
        json_fields = json.loads(model.metadata)

        metadata.update(json_fields)

        for enhanced_meta in model.enhanced_meta.all():
            metadata.update({enhanced_meta.key: enhanced_meta.value})
        return metadata

    def replace_dataset_theme(self, dataset_meta: dict):
        """Reemplaza los 'id' de los themes en los metadatos del dataset
        pasado por un dict con el detalle de cada theme (el id, su label
        y descripción)
        """
        if not self.field.distribution.dataset.themes:
            return

        themes: list = dataset_meta.get('theme', [])
        theme_details: list = json.loads(self.field.distribution.dataset.themes)
        dataset_meta['theme'] = []
        for theme_id in themes:
            for theme_dict in theme_details:
                if theme_id == theme_dict['id']:
                    dataset_meta['theme'].append(theme_dict)
