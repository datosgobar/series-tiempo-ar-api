from django.test import TestCase
from django.conf import settings
from elastic_spike.apps.api.query import Query


class QueryTest(TestCase):
    start = settings.API_DEFAULT_VALUES['start']
    limit = settings.API_DEFAULT_VALUES['limit']

    default_limit = 10
    max_limit = 1000

    start_date = 2010
    end_date = 2015

    def setUp(self):
        self.query = Query()

    def test_inicialmente_no_hay_series(self):
        self.assertFalse(self.query.series)

    def test_pagination_agrega_serie_si_no_existe(self):
        self.query.add_pagination(self.start, self.limit)

        self.assertEqual(len(self.query.series), 1)

    def test_pagination_no_agrega_serie_si_ya_existe_una(self):
        self.query.add_pagination(self.start, self.limit)
        self.query.add_pagination(self.start, self.limit)

        self.assertEqual(len(self.query.series), 1)

    def test_pagination(self):
        self.query.add_pagination(self.start, self.limit)
        self.query.run()

        self.assertEqual(len(self.query.data), self.limit - self.start)

    def test_pagination_limit(self):
        self.query.add_pagination(self.start, self.max_limit)
        self.query.run()
        self.assertEqual(len(self.query.data), self.max_limit - self.start)
    #
    # def test_time_filter(self):
    #     self.query.add_filter(self.start_date, self.end_date)
    #     self.query.add_series('random-0', 'value')
    #     self.query.run()
    #     for row in self.query.data:
    #         date = row[0]
    #         self.assertGreaterEqual(datetime.strptime(str(date), '%Y'),
    #                                 datetime.strptime(str(self.start_date), '%Y'))
    #         self.assertLessEqual(datetime.strptime(str(date), '%Y'),
    #                              datetime.strptime(str(self.end_date), '%Y'))

    def test_execute_single_series(self):
        self.query.run()

        self.assertTrue(self.query.data)

    def test_default_return_limits(self):
        self.query.run()

        self.assertEqual(len(self.query.data), self.default_limit)

    def test_add_series(self):
        self.query.add_series('random-0', 'value')
        self.query.run()

        self.assertTrue(self.query.data)
        # Expected: rows de 2 datos: timestamp, valor de la serie
        self.assertTrue(len(self.query.data[0]) == 2)

    def test_add_two_series(self):
        self.query.add_series('random-0', 'value')
        self.query.add_series('random-0', 'percent_change')
        self.query.run()

        self.assertTrue(self.query.data)
        # Expected: rows de 3 datos: timestamp, serie 1, serie 2
        self.assertTrue(len(self.query.data[0]) == 3)