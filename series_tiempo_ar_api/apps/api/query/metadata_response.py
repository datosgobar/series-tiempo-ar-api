#! coding: utf-8
import json
from typing import Union, Dict

from django_datajsonar.models import Field, Catalog, Dataset, Distribution

from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.metadata.models import SeriesUnits


class MetadataResponse:
    datajson_entity = Union[Catalog, Dataset, Distribution, Field]

    def __init__(self, field: Field, simple: bool, flat: bool):
        self.field = field
        self.simple = simple
        self.flat = flat

    def get_response(self):
        metadata = self._get_full_metadata()

        if self.simple:
            _filter_keys(metadata['catalog'], constants.CATALOG_SIMPLE_META_FIELDS)
            _filter_keys(metadata['dataset'], constants.DATASET_SIMPLE_META_FIELDS)
            _filter_keys(metadata['distribution'], constants.DISTRIBUTION_SIMPLE_META_FIELDS)
            _filter_keys(metadata['field'], constants.FIELD_SIMPLE_META_FIELDS)

        if self.flat:
            metadata = _flatten_metadata(metadata)

        return metadata

    def _get_full_metadata(self):
        distribution = self.field.distribution
        dataset = distribution.dataset
        catalog = dataset.catalog

        dataset_meta = self._get_full_metadata_for_model(dataset)
        self.replace_dataset_theme(dataset_meta)

        return {
            'catalog': self._get_full_metadata_for_model(catalog),
            'dataset': dataset_meta,
            'distribution': self._get_full_metadata_for_model(distribution),
            'field': self._field_metadata(self.field),
        }

    def _field_metadata(self, field: Field):
        metadata = self._get_full_metadata_for_model(field)
        if self.simple:
            return metadata

        metadata.update({'is_percentage': False})
        units = metadata.get('units')

        if not units:
            return metadata

        try:
            series_units = SeriesUnits.objects.get(name=units)
        except SeriesUnits.DoesNotExist:
            return metadata

        metadata['is_percentage'] = series_units.percentage
        return metadata

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


def _flatten_metadata(metadata: Dict[str, Dict]) -> dict:
    result = {}
    for level, level_meta in metadata.items():
        for meta_field, value in level_meta.items():
            flat_key = f'{level}_{meta_field}'
            result[flat_key] = value

    return result


def _filter_keys(metadata, allowed_fields):
    for meta_field in list(metadata):
        if meta_field not in allowed_fields:
            metadata.pop(meta_field)
