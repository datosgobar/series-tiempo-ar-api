#! coding: utf-8
import mock
from datetime import datetime
from series_tiempo_ar_api.apps.management import meta_keys


class MockData:
    id = 'algo'
    description = 'description'
    title = 'title'
    dataset_title = 'data_title'
    dataset_publisher_name = 'pub_name'
    periodicity = 'mensual'
    units = 'unidades'
    dataset_source = 'fuente'
    start_date = datetime(2018, 1, 1, 0, 0, 0)
    end_date = datetime(2018, 7, 12, 0, 0, 0)

    class Hits:
        total = 1

    hits = Hits().total


def get_aggregation_mock_search():
    search = get_mock_search()
    agg = mock.MagicMock()
    agg.aggregations.results.buckets = [{'key': 'test_value', 'doc_count': 1}]

    search.__iter__.return_value = search.__iter__ + 4 * [agg]


def get_mock_search():
    mock_search = mock.MagicMock()
    mock_search.hits.total = 1
    mock_search.__iter__.return_value = [MockData()]

    mock_multi_search = mock.MagicMock()
    mock_multi_search.__getitem__.return_value = mock_search
    return mock_multi_search
