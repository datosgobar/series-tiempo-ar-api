#! coding: utf-8
import mock
from datetime import datetime
from series_tiempo_ar_api.apps.management import meta_keys


class MockData:
    def __init__(self):
        self.id = 'algo'
        self.description = 'description'
        self.title = 'title'
        self.dataset_title = 'data_title'
        self.dataset_publisher_name = 'pub_name'
        setattr(self, meta_keys.PERIODICITY, 'mensual')
        self.units = 'unidades'
        self.dataset_source = 'fuente'
        setattr(self, meta_keys.INDEX_START, datetime(2018, 1, 1, 0, 0, 0))
        setattr(self, meta_keys.INDEX_END,datetime(2018, 7, 12, 0, 0, 0))


def get_mock_search():
    mock_search = mock.MagicMock()
    mock_search.hits.total = 1
    mock_search.__iter__.return_value = [MockData()]
    return mock_search
