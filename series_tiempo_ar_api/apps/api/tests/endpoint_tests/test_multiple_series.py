from series_tiempo_ar_api.apps.api.tests.endpoint_tests.endpoint_test_case import EndpointTestCase


class MultipleSeriesTests(EndpointTestCase):

    def test_none_first_date(self):
        ids = f'{self.increasing_year_series_id},{self.increasing_year_series_id_2004}'
        resp = self.run_query({'ids': ids})

        data = [
            ['1999-01-01', 100, None],
            ['2000-01-01', 101, None],
            ['2001-01-01', 102, None],
            ['2002-01-01', 103, None],
            ['2003-01-01', 104, None],
            ['2004-01-01', 105, 100],
            ['2005-01-01', 106, 101],
            ['2006-01-01', 107, 102],
            ['2007-01-01', 108, 103],
            ['2008-01-01', 109, 104],
            ['2009-01-01', None, 105],
            ['2010-01-01', None, 106],
            ['2011-01-01', None, 107],
            ['2012-01-01', None, 108],
            ['2013-01-01', None, 109],
        ]

        self.assertEqual(resp['data'], data)
