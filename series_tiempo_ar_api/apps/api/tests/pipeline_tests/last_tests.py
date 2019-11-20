import iso8601
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.api.query.pipeline import Last
from series_tiempo_ar_api.apps.api.tests.helpers import get_series_id

SERIES_NAME = get_series_id('month')


class LastTests(TestCase):
    single_series = SERIES_NAME

    def setUp(self):
        self.query = Query()
        self.cmd = Last()

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(identifier=cls.single_series)
        super(cls, LastTests).setUpClass()

    def test_last_cmd(self):
        self.query.add_series(self.field)
        self.cmd.run(self.query, {'last': '10'})

        orig_query = Query()
        orig_query.add_series(self.field)
        orig_query.sort('desc')
        data = orig_query.run()['data']
        data.reverse()

        reverse_data = self.query.run()['data']

        self.assertListEqual(data[-10:], reverse_data)

    def test_last_cmd_with_start_date(self):
        rows = 100
        self.query.add_series(self.field)
        self.cmd.run(self.query, {'last': str(rows)})

        orig_query = Query()
        orig_query.add_series(self.field)
        orig_query.sort('desc')
        data = orig_query.run()['data']
        last_date = iso8601.parse_date(data[-1][0])

        start_date = last_date - relativedelta(years=1)
        self.query.add_filter(start_date=start_date, end_date=None)

        data = self.query.run()['data']
        self.assertTrue(len(data), 12)

    def test_sort_mutual_exclusion(self):
        self.cmd.run(self.query, {'last': '10',
                                  'sort': 'asc'})
        self.assertTrue(self.cmd.errors)

    def test_start_mutual_exclusion(self):
        self.cmd.run(self.query, {'last': '10',
                                  'start': '10'})
        self.assertTrue(self.cmd.errors)

    def test_limit_mutual_exclusion(self):
        self.cmd.run(self.query, {'last': '10',
                                  'limit': '10'})
        self.assertTrue(self.cmd.errors)

    def test_invalid_last(self):
        self.cmd.run(self.query, {'last': 'not_a_number'})
        self.assertTrue(self.cmd.errors)

    def test_last_over_limit(self):
        self.cmd.run(self.query, {'last': '999999'})
        self.assertTrue(self.cmd.errors)

    def test_last_negative(self):
        self.cmd.run(self.query, {'last': '-10'})
        self.assertTrue(self.cmd.errors)
