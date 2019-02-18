from django.test import TestCase

from series_tiempo_ar_api.apps.analytics.elasticsearch.index import get_params


class QueryParserTests(TestCase):

    def test_parse_serie_string_params(self):
        string = 'test_serie'

        params = get_params(string)
        self.assertDictEqual(params, {'ids': string})

    def test_parse_serie_string_with_rep_mode(self):
        serie_id = 'test_serie'
        rep_mode = 'value'

        string = f'{serie_id}:{rep_mode}'
        params = get_params(string)
        self.assertDictEqual(params, {'ids': string, 'representation_mode': rep_mode})

    def test_parse_serie_string_with_collapse_agg(self):
        serie_id = 'test_serie'
        agg = 'max'

        string = f'{serie_id}:{agg}'
        params = get_params(string)
        self.assertDictEqual(params, {'ids': string, 'collapse_aggregation': agg})

    def test_parse_all_three(self):
        serie_id = 'test_serie'
        rep_mode = 'value'
        agg = 'max'

        string = f'{serie_id}:{rep_mode}:{agg}'
        params = get_params(string)
        self.assertDictEqual(params, {'ids': string,
                                      'representation_mode': rep_mode,
                                      'collapse_aggregation': agg})

    def test_parse_all_three_different_order(self):
        serie_id = 'test_serie'
        rep_mode = 'value'
        agg = 'max'

        string = f'{serie_id}:{agg}:{rep_mode}'
        params = get_params(string)
        self.assertDictEqual(params, {'ids': string,
                                      'representation_mode': rep_mode,
                                      'collapse_aggregation': agg})

    def test_invalid_params_are_ignored(self):
        serie_id = 'test_serie'
        rep_mode = 'invalid_value'

        string = f'{serie_id}:{rep_mode}'
        params = get_params(string)
        self.assertDictEqual(params, {'ids': string})
