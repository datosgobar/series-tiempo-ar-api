import mock
from django.test import TestCase

from series_tiempo_ar_api.apps.management.models import APIIndexingConfig
from series_tiempo_ar_api.libs.indexing.api_index_enqueue import api_index_enqueue


def test_function():
    return 1 + 1


@mock.patch('series_tiempo_ar_api.libs.indexing.api_index_enqueue.get_queue')
class APIIndexEnqueueTests(TestCase):
    def setUp(self) -> None:
        self.timeout = APIIndexingConfig.get_solo().indexing_timeout
        self.function = test_function

    def test_queue_called(self, queue):
        api_index_enqueue(self.function)
        queue().enqueue_call.assert_called_once()

    def test_assert_enqueue_called_with_same_args(self, queue):
        args = (1, )
        api_index_enqueue(self.function, *args)
        queue().enqueue_call.assert_called_with(self.function, args, {}, timeout=self.timeout)

    def test_assert_enqueue_called_with_same_kwargs(self, queue):
        kwargs = {'key': 1}
        api_index_enqueue(self.function, **kwargs)
        queue().enqueue_call.assert_called_with(self.function, tuple(), kwargs, timeout=self.timeout)

    def test_enqueue_called_with_timeout_from_config(self, queue):
        api_index_enqueue(self.function)
        timeout = queue().enqueue_call.call_args[1]['timeout']
        self.assertEqual(timeout, self.timeout)
