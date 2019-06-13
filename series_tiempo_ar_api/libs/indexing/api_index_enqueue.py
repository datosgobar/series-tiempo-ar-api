from django_rq import get_queue

from series_tiempo_ar_api.apps.management.models import APIIndexingConfig

API_INDEX_QUEUE = 'api_index'


def api_index_enqueue(function, *args, **kwargs):
    timeout = APIIndexingConfig.get_solo().indexing_timeout
    get_queue(API_INDEX_QUEUE).enqueue_call(function, args, kwargs, timeout=timeout)
