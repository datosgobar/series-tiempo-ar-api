#! coding: utf-8

from django_datajsonar.models import Field, Node, Metadata, ContentType

from series_tiempo_ar_api.apps.api.helpers import get_periodicity_human_format_es
from series_tiempo_ar_api.apps.management import meta_keys
from elasticsearch.helpers import parallel_bulk

from series_tiempo_ar_api.apps.metadata.models import IndexMetadataTask
from series_tiempo_ar_api.libs.indexing.elastic import ElasticInstance


class EnhancedMetaIndexer:

    def __init__(self, node: Node, task: IndexMetadataTask, doc_type):
        self.node = node
        self.task = task
        self.doc_type = doc_type
        self.elastic = ElasticInstance.get()

    def index(self):
        field_content_type = ContentType.objects.get_for_model(Field)
        available_fields = Metadata.objects.filter(
            key=meta_keys.AVAILABLE,
            value='true',
            content_type=field_content_type).values_list('object_id', flat=True)
        fields = Field.objects.filter(
            id__in=available_fields,
        )

        actions = []
        for field in fields:
            periodicity = meta_keys.get(field, meta_keys.PERIODICITY)
            start_date = meta_keys.get(field, meta_keys.INDEX_START)
            end_date = meta_keys.get(field, meta_keys.INDEX_END)

            doc = self.doc_type(
                periodicity=get_periodicity_human_format_es(periodicity),
                start_date=start_date,
                end_date=end_date,
            )

            doc.meta.id = field.identifier
            # Adaptamos el formato del dict para usarlo en update
            # Ver https://stackoverflow.com/a/35184099
            action = doc.to_dict(include_meta=True)
            action['_op_type'] = 'update'
            action['_source'] = {'doc': action['_source']}
            actions.append(action)

        for success, info in parallel_bulk(self.elastic, actions):
            if not success:
                self.task.info(self.task, 'Error indexando: {}'.format(info))
