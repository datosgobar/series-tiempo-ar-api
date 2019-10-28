#! coding: utf-8
from django.conf import settings
from django.test import TestCase
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.api.query.pipeline import \
    IdsField
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.query.strings import SERIES_DOES_NOT_EXIST
from series_tiempo_ar_api.apps.management import meta_keys
from ..helpers import get_series_id
from ..support.pipeline import time_serie_name

SERIES_NAME = get_series_id('month')


class IdsTest(TestCase):
    """Testea el comando que se encarga del parámetro 'ids' de la
    query: el parseo de IDs de series y modos de representación de las
    mismas.
    """
    single_series = SERIES_NAME
    single_series_rep_mode = SERIES_NAME + ':percent_change'

    multi_series = SERIES_NAME + ',' + SERIES_NAME

    @classmethod
    def setUpClass(cls):
        super(cls, IdsTest).setUpClass()

    def setUp(self):
        self.cmd = IdsField()
        self.query = Query()

    def test_invalid_series(self):
        invalid_series = 'invalid'
        self.cmd.run(self.query, {'ids': invalid_series})
        self.assertTrue(self.cmd.errors)

    def test_serie_does_not_exist_message(self):
        invalid_series = time_serie_name()
        self.cmd.run(self.query, {'ids': invalid_series})
        base_msg = SERIES_DOES_NOT_EXIST.format('')
        self.assertIn(base_msg, self.cmd.errors[0]["error"])

    def test_valid_series(self):
        self.cmd.run(self.query, {'ids': self.single_series})
        self.assertFalse(self.cmd.errors)

    def test_global_rep_mode(self):
        self.cmd.run(self.query, {'ids': self.single_series})
        self.query.sort('asc')
        data = self.query.run()['data']

        change_query = Query()
        self.cmd.run(change_query, {'ids': self.single_series,
                                    'representation_mode': 'change'})

        change_query.sort('asc')
        # Un valor menos que la query original, 99 variaciones para 100 valores
        change_query.add_pagination(start=0, limit=99)
        change_data = change_query.run()['data']

        for index, row in enumerate(change_data):
            change = data[index + 1][1] - data[index][1]
            # La resta anterior trae pérdida de precisión si los números de 'data' son grandes
            self.assertAlmostEqual(row[1], change, places=5)

    def test_multiple_series(self):
        self.cmd.run(self.query, {'ids': self.multi_series})
        data = self.query.run()['data']

        self.assertTrue(len(data[0]), 3)

    def test_leading_comma(self):
        self.cmd.run(self.query, {'ids': ',' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_final_comma(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ','})
        self.assertTrue(self.cmd.errors)

    def test_one_valid_one_invalid(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ',invalid'})
        self.assertTrue(self.cmd.errors)

    def test_second_valid_first_invalid(self):
        self.cmd.run(self.query, {'ids': 'invalid,' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_invalid_rep_mode(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ':' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_leading_semicolon(self):
        self.cmd.run(self.query, {'ids': ':' + SERIES_NAME})
        self.assertTrue(self.cmd.errors)

    def test_final_semicolon(self):
        self.cmd.run(self.query, {'ids': SERIES_NAME + ':'})
        self.assertTrue(self.cmd.errors)

    def test_three_params(self):
        ids = SERIES_NAME + ':value:sum'
        self.cmd.run(self.query, {'ids': ids})

        self.assertListEqual(self.cmd.errors, [])

    def test_only_agg(self):
        ids = SERIES_NAME + ':sum'
        self.cmd.run(self.query, {'ids': ids})

        self.assertListEqual(self.cmd.errors, [])

    def test_invalid_collapse_agg(self):
        ids = SERIES_NAME + ':change:invalid_agg'
        self.cmd.run(self.query, {'ids': ids})

        self.assertTrue(self.cmd.errors)

    def test_more_than_three_params(self):
        ids = SERIES_NAME + ':value:sum:other'
        self.cmd.run(self.query, {'ids': ids})

        self.assertTrue(self.cmd.errors)

    def test_empty_param(self):
        ids = SERIES_NAME + ':value::'
        self.cmd.run(self.query, {'ids': ids})

        self.assertTrue(self.cmd.errors)

    def test_no_series(self):
        ids = 'value:sum'
        self.cmd.run(self.query, {'ids': ids})

        self.assertTrue(self.cmd.errors)

    def test_series_over_limit(self):

        ids_list = [SERIES_NAME] * (settings.MAX_ALLOWED_VALUES['ids'] + 1)
        ids = ids_list[0]
        for series_id in ids_list[1:]:
            ids += ',' + series_id

        self.cmd.run(self.query, {'ids': ids})

        self.assertTrue(self.cmd.errors)

    def test_invalid_series_field(self):
        invalid_series = 'invalid'
        self.cmd.run(self.query, {'ids': invalid_series})
        self.assertIn(invalid_series, self.cmd.failed_series)

    def test_multiple_series_one_invalid(self):
        invalid = 'invalid'
        multi_series = f'{self.single_series},{invalid}'

        self.cmd.run(self.query, {'ids': multi_series})
        self.assertIn(invalid, self.cmd.failed_series)

    def test_serie_without_index_start(self):
        Field.objects.get(identifier=self.single_series).enhanced_meta.get(key=meta_keys.INDEX_START).delete()
        self.cmd.run(self.query, {'ids': self.single_series})

        self.assertTrue(self.cmd.errors)

    def test_non_present_series(self):
        Field.objects.filter(identifier=self.single_series).update(present=False)
        self.cmd.run(self.query, {'ids': self.single_series})
        self.assertFalse(self.cmd.errors)
