#! coding: utf-8
import mock


def get_mock_search():
    mock_search = mock.MagicMock()
    mock_search.hits.total = 1
    mock_search.__iter__.return_value = [{
        'id': 'algo',
        'description': 'description',
        'title': 'title',
        'dataset_title': 'data_title',
        'dataset_publisher_name': 'pub_name',
    }]
    return mock_search
