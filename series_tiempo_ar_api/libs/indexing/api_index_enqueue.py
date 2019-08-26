from django_rq import get_queue

from series_tiempo_ar_api.apps.management.models import APIIndexingConfig

API_INDEX_QUEUE = 'api_index'


def api_index_enqueue(function, *args, **kwargs):
    timeout = APIIndexingConfig.get_solo().indexing_timeout
    queue_name = API_INDEX_QUEUE
    enqueue_job_with_timeout(queue_name, function, timeout, args, kwargs)


def enqueue_job_with_timeout(queue_name, function, timeout, args=None, kwargs=None):
    get_queue(queue_name).enqueue_call(function, args, kwargs, timeout=timeout)
