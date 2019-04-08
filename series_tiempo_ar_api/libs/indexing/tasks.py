#! coding: utf-8
import logging
from traceback import format_exc

from django.conf import settings
from django.db import transaction
from django_rq import job

from django_datajsonar.models import Node
from django_datajsonar.models import Distribution

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.management.models import IndexDataTask
from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.indexing.indexer.data_frame import init_df, get_distribution_time_index_periodicity
from series_tiempo_ar_api.libs.indexing.indexer.distribution_indexer import DistributionIndexer
from series_tiempo_ar_api.libs.indexing.indexer.metadata import calculate_enhanced_meta
from series_tiempo_ar_api.libs.indexing.indexer.utils import remove_duplicated_fields
from series_tiempo_ar_api.libs.indexing.popularity import update_popularity_metadata
from .report.report_generator import ReportGenerator
from .distribution_validator import DistributionValidator


logger = logging.getLogger(__name__)


@job('api_index', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(distribution_id, node_id, task_id,
                       read_local=False, index=settings.TS_INDEX, force=False):

    node = Node.objects.get(id=node_id)
    task = IndexDataTask.objects.get(id=task_id)
    distribution_model = Distribution.objects.get(identifier=distribution_id,
                                                  dataset__catalog__identifier=node.catalog_id,
                                                  present=True)

    try:
        DistributionValidator(read_local).run(distribution_model)

        changed = True
        _hash = distribution_model.enhanced_meta.filter(key=meta_keys.LAST_HASH)
        if _hash:
            changed = _hash[0].value != distribution_model.data_hash

        if changed or force:
            DistributionIndexer(index=index).reindex(distribution_model)

        update_distribution_metadata(changed, distribution_model)

    except Exception as e:
        _handle_exception(distribution_model.dataset, distribution_id, e, node, task)


def update_distribution_metadata(changed, distribution_model):
    time_index = DistributionRepository(distribution_model).get_time_index_series()
    df = init_df(distribution_model, time_index)

    periodicity = get_distribution_time_index_periodicity(time_index)
    for serie in df.columns:
        meta = calculate_enhanced_meta(df[serie], periodicity)

        field = distribution_model.field_set.get(identifier=serie, present=True)
        for meta_key, value in meta.items():
            field.enhanced_meta.update_or_create(key=meta_key, defaults={'value': value})

    distribution_model.enhanced_meta.update_or_create(key=meta_keys.LAST_HASH,
                                                      defaults={'value': distribution_model.data_hash})
    distribution_model.enhanced_meta.update_or_create(key=meta_keys.CHANGED,
                                                      defaults={'value': str(changed)})
    update_popularity_metadata(distribution_model)
    remove_duplicated_fields(distribution_model)


def _handle_exception(dataset_model, distribution_id, exc, node, task):
    msg = u"Excepción en distrbución {} del catálogo {}: {}"
    if exc:
        e_msg = exc
    else:
        e_msg = format_exc()
    msg = msg.format(distribution_id, node.catalog_id, e_msg)
    IndexDataTask.info(task, msg)
    logger.info(msg)

    with transaction.atomic():
        try:
            distribution = Distribution.objects.get(identifier=distribution_id,
                                                    dataset__catalog__identifier=node.catalog_id,
                                                    present=True)
            distribution.error_msg = msg
            distribution.error = True
            distribution.field_set.update(error=True)
            distribution.save()
        except Distribution.DoesNotExist:
            pass

    # No usamos un contador manejado por el indicator_loader para asegurarse que los datasets
    # sean contados una única vez (pueden fallar una vez por cada una de sus distribuciones)
    dataset_model.error = True
    dataset_model.save()

    dataset_model.catalog.error = True
    dataset_model.catalog.save()

    if settings.RQ_QUEUES['indexing'].get('ASYNC', True):
        raise exc  # Django-rq / sentry logging


@job("api_report", timeout=-1)
def send_indexation_report_email(*_):
    task = IndexDataTask.objects.last()
    ReportGenerator(task).generate()
