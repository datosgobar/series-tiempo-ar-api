#! coding: utf-8
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from pydatajson import DataJson
from django_datajsonar.models import Field, Node, Metadata, ContentType

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.metadata import constants
from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class CatalogMetadataIndexer:

    def __init__(self, node: Node, task: IndexMetadataTask, index: str):
        self.node = node
        self.task = task
        self.index_name = index
        self.elastic: Elasticsearch = ElasticInstance.get()
        self.fields_meta = {}
        self.init_fields_meta_cache()
        try:
            data_json = DataJson(node.catalog_url)
            themes = data_json['themeTaxonomy']
            self.themes = self.get_themes(themes)
        except Exception:
            raise ValueError("Error de lectura de los themes del catálogo")

    def index(self):
        if not self.get_available_fields().count():
            self.task.info(self.task, "No hay series para indexar en este catálogo")
            return False

        index_ok = False
        for success, info in streaming_bulk(self.elastic, self.generate_actions()):
            if not success:
                self.task.info(self.task, 'Error indexando: {}'.format(info))
            else:
                index_ok = True
        return index_ok

    def generate_actions(self):
        fields = self.get_available_fields()

        for field in fields:
            periodicity = self.fields_meta[field.id].get(meta_keys.PERIODICITY)
            start_date = self.fields_meta[field.id].get(meta_keys.INDEX_START)
            end_date = self.fields_meta[field.id].get(meta_keys.INDEX_END)

            if not periodicity or not start_date or not end_date:
                msg = "Metadatos enriquecidos faltantes en serie {} ({})" \
                    .format(field.identifier, field.distribution.identifier)
                self.task.info(self.task, msg)

            field_meta = json.loads(field.metadata)
            dataset = json.loads(field.distribution.dataset.metadata)
            doc = self.generate_es_doc(
                field.identifier,
                periodicity=periodicity,
                start_date=start_date,
                end_date=end_date,
                title=field_meta.get('title'),
                description=field_meta.get('description'),
                id=field_meta.get('id'),
                units=field_meta.get('units'),
                dataset_title=dataset.get('title'),
                dataset_source=dataset.get('source'),
                dataset_source_keyword=dataset.get('source'),
                dataset_description=dataset.get('description'),
                dataset_publisher_name=dataset.get('publisher', {}).get('name'),
                dataset_theme=self.themes.get(dataset.get('theme', [None])[0]),
                catalog_id=self.node.catalog_id
            )

            yield doc

    def get_available_fields(self):
        field_content_type = ContentType.objects.get_for_model(Field)
        available_fields = Metadata.objects.filter(
            key=meta_keys.AVAILABLE,
            value='true',
            content_type=field_content_type).values_list('object_id', flat=True)
        fields = Field.objects.filter(
            distribution__dataset__catalog__identifier=self.node.catalog_id,
            id__in=available_fields,
            present=True,
            error=False,
        )
        return fields

    def init_fields_meta_cache(self):
        field_content_type = ContentType.objects.get_for_model(Field)
        metas = Metadata.objects.filter(
            content_type=field_content_type)

        for metadata in metas:
            self.fields_meta.setdefault(metadata.object_id, {})[metadata.key] = metadata.value

    @staticmethod
    def get_themes(theme_taxonomy):
        themes = {}
        for theme in theme_taxonomy:
            themes[theme['id']] = theme['label']

        return themes

    def generate_es_doc(self, doc_id, **kwargs):
        return {
            '_id': doc_id,
            '_index': self.index_name,
            '_type': constants.METADATA_DOC_TYPE,
            '_source': kwargs
        }
