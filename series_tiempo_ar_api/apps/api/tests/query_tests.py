#! coding: utf-8
import json

import iso8601
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.api.exceptions import CollapseError
from series_tiempo_ar_api.apps.api.query.query import Query
from series_tiempo_ar_api.apps.metadata.models import SeriesUnits
from .helpers import get_series_id

SERIES_NAME = get_series_id('month')


class QueryTests(TestCase):
    single_series = SERIES_NAME

    def setUp(self):
        self.field = Field.objects.get(identifier=self.single_series)
        self.query = Query()

    def test_index_metadata_frequency(self):
        self.query.add_series(self.field)
        meta = self.query.run()['meta']

        index_frequency = meta[0]['frequency']
        self.assertEqual(index_frequency, 'month')

    def test_index_metadata_start_end_dates(self):
        self.query.add_series(self.field)
        res = self.query.run()

        index_meta = res['meta'][0]
        self.assertEqual(res['data'][0][0], index_meta['start_date'])
        self.assertEqual(res['data'][-1][0], index_meta['end_date'])

    def test_collapse_index_metadata_frequency(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.field)
        self.query.update_collapse(collapse=collapse_interval)
        meta = self.query.run()['meta']

        index_frequency = meta[0]['frequency']
        self.assertEqual(index_frequency, collapse_interval)

    def test_collapse_index_metadata_start_end_dates(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.field)
        self.query.update_collapse(collapse=collapse_interval)
        res = self.query.run()
        data = res['data']

        index_meta = res['meta'][0]
        self.assertEqual(data[0][0], index_meta['start_date'])
        self.assertEqual(data[-1][0], index_meta['end_date'])

    @raises(CollapseError)
    def test_invalid_collapse(self):
        collapse_interval = 'day'  # Serie cargada es mensual
        self.query.add_series(self.field)
        self.query.update_collapse(collapse=collapse_interval)

    def test_identifiers(self):

        self.query.add_series(self.field)
        # Devuelve lista de ids, una por serie. Me quedo con la primera (única)
        ids = self.query.get_series_identifiers()[0]
        field = Field.objects.get(identifier=self.single_series)
        self.assertEqual(ids['id'], field.identifier)
        self.assertEqual(ids['distribution'], field.distribution.identifier)
        self.assertEqual(ids['dataset'], field.distribution.dataset.identifier)

    def test_weekly_collapse(self):
        day_series_name = settings.TEST_SERIES_NAME.format('day')
        field = Field.objects.get(identifier=day_series_name)

        self.query.add_series(field)

        self.query.update_collapse(collapse='week')
        self.query.sort(how='asc')
        data = self.query.run()['data']

        first_date = iso8601.parse_date(data[0][0])
        second_date = iso8601.parse_date(data[1][0])

        delta = second_date - first_date
        self.assertEqual(delta.days, 7)

    def test_simple_metadata_remove_catalog(self):
        catalog = self.field.distribution.dataset.catalog
        catalog.metadata = '{"title": "test_title", "extra_field": "extra"}'
        catalog.save()

        self.query.add_series(self.field)
        meta = self.query.run()['meta']
        index_meta = meta[1]['catalog']
        self.assertNotIn('extra_field', index_meta)
        self.assertIn('title', index_meta)

    def test_simple_metadata_remove_dataset(self):
        dataset = self.field.distribution.dataset
        dataset.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dataset.save()

        self.query.add_series(self.field)
        meta = self.query.run()['meta']
        index_meta = meta[1]['dataset']
        self.assertNotIn('extra_field', index_meta)
        self.assertIn('title', index_meta)

    def test_simple_metadata_remove_distribution(self):
        dist = self.field.distribution
        dist.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dist.save()

        self.query.add_series(self.field)
        meta = self.query.run()['meta']
        index_meta = meta[1]['distribution']
        self.assertNotIn('extra_field', index_meta)
        self.assertIn('title', index_meta)

    def test_simple_metadata_remove_field(self):
        self.field.metadata = '{"id": "test_title", "extra_field": "extra"}'

        self.query.add_series(self.field)
        meta = self.query.run()['meta']
        index_meta = meta[1]['field']
        self.assertNotIn('extra_field', index_meta)
        self.assertIn('id', index_meta)

    def test_flatten_metadata_response(self):
        catalog = self.field.distribution.dataset.catalog
        catalog.metadata = '{"title": "test_title", "extra_field": "extra"}'
        catalog.save()

        dataset = self.field.distribution.dataset
        dataset.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dataset.save()

        dist = self.field.distribution
        dist.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dist.save()

        self.field.metadata = '{"id": "test_title", "extra_field": "extra"}'

        self.query.add_series(self.field)
        self.query.flatten_metadata_response()
        flat_meta = self.query.run()['meta'][1]

        other_query = Query()
        other_query.add_series(self.field)
        meta = other_query.run()['meta'][1]

        for key in meta:
            for in_key in meta[key]:
                self.assertEqual(meta[key][in_key], flat_meta['{}_{}'.format(key, in_key)])

    def test_full_metadata_flat_response(self):
        catalog = self.field.distribution.dataset.catalog
        catalog.metadata = '{"title": "test_title", "extra_field": "extra"}'
        catalog.save()

        dataset = self.field.distribution.dataset
        dataset.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dataset.save()

        dist = self.field.distribution
        dist.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dist.save()

        self.field.metadata = '{"id": "test_title", "extra_field": "extra"}'

        self.query.add_series(self.field)
        self.query.set_metadata_config('full')
        self.query.flatten_metadata_response()
        flat_meta = self.query.run()['meta'][1]

        other_query = Query()
        other_query.add_series(self.field)
        other_query.set_metadata_config('full')
        meta = other_query.run()['meta'][1]

        for key in meta:
            for in_key in meta[key]:
                self.assertEqual(meta[key][in_key], flat_meta['{}_{}'.format(key, in_key)])

    def test_full_metadata_includes_enhanced_meta(self):
        self.query.add_series(self.field)
        self.query.set_metadata_config('full')
        meta = self.query.run()['meta']

        for enhanced_meta in self.field.enhanced_meta.all():
            self.assertEqual(meta[1]['field'][enhanced_meta.key], enhanced_meta.value)

    def test_full_metadata_periodicty_with_collapse(self):
        self.query.add_series(self.field)
        self.query.update_collapse('year')
        self.query.set_metadata_config('full')

        resp = self.query.run()

        self.assertEqual(resp['meta'][0]['frequency'], 'year')
        self.assertEqual(resp['meta'][1]['field'][meta_keys.PERIODICITY],
                         meta_keys.get(self.field, meta_keys.PERIODICITY))

    def test_query_count(self):
        self.query.add_series(self.field)

        resp = self.query.run()

        # Longitud de la serie pedida. Ver support/generate_data.py
        self.assertEqual(resp['count'], 12 * 10)

    def test_day_series_length_with_limit_and_rep_mode(self):
        day_series_name = settings.TEST_SERIES_NAME.format('day')
        field = Field.objects.get(identifier=day_series_name)

        self.query.add_series(field, rep_mode='percent_change_a_year_ago')
        self.query.add_pagination(start=0, limit=2)
        result = self.query.run()

        self.assertEqual(len(result['data']), 2)

    def test_response_rep_mode_units(self):
        self.query.add_series(self.field)

        meta = self.query.run()['meta']
        field_meta = meta[1]['field']
        self.assertEqual(field_meta['representation_mode'], 'value')
        self.assertEqual(field_meta['representation_mode_units'], meta[1]['field'].get('units'))

    def test_response_rep_mode_units_pct_change(self):
        rep_mode = constants.PCT_CHANGE
        self.query.add_series(self.field, rep_mode=rep_mode)

        meta = self.query.run()['meta']
        field_meta = meta[1]['field']

        self.assertEqual(field_meta['representation_mode'], rep_mode)
        self.assertEqual(field_meta['representation_mode_units'], constants.VERBOSE_REP_MODES[rep_mode])

    def test_aggregation_on_yearly_series(self):
        """Esperado: Valores de la serie con y sin agregación son iguales, no
        hay valores que colapsar"""
        year_series = get_series_id('year')
        field = Field.objects.get(identifier=year_series)
        self.query.add_series(field)
        self.query.add_series(field, collapse_agg='end_of_period')

        data = self.query.run()['data']

        for row in data:
            self.assertEqual(row[1], row[2])

    def test_aggregation_on_monthly_series(self):
        """Esperado: Valores de la serie con y sin agregación son iguales, no
        hay valores que colapsar"""
        self.query.add_series(self.field)
        self.query.add_series(self.field, collapse_agg='end_of_period')

        data = self.query.run()['data']

        for row in data:
            self.assertEqual(row[1], row[2])

    def test_same_series_multiple_times_different_rep_mode(self):
        self.query.add_series(self.field)
        self.query.add_series(self.field, rep_mode='percent_change')
        self.query.set_metadata_config(how=constants.METADATA_ONLY)
        meta = self.query.run()['meta']

        self.assertEqual(meta[1]['field']['representation_mode'], 'value')
        self.assertEqual(meta[2]['field']['representation_mode'], 'percent_change')

    def test_is_percentage(self):
        SeriesUnits.objects.create(name=json.loads(self.field.metadata)['units'],
                                   percentage=True)
        self.query.add_series(self.field)
        self.query.set_metadata_config(how=constants.METADATA_ONLY)
        meta = self.query.run()['meta']

        self.assertTrue(meta[1]['field']['is_percentage'])

    def test_is_percentage_units_false(self):
        SeriesUnits.objects.create(name=json.loads(self.field.metadata)['units'],
                                   percentage=False)
        self.query.add_series(self.field)
        self.query.set_metadata_config(how=constants.METADATA_ONLY)
        meta = self.query.run()['meta']

        self.assertFalse(meta[1]['field']['is_percentage'])

    def test_is_percentage_with_percentage_rep_mode(self):
        self.query.add_series(self.field, rep_mode=constants.PCT_CHANGE)
        self.query.set_metadata_config(how=constants.METADATA_ONLY)
        meta = self.query.run()['meta']

        self.assertTrue(meta[1]['field']['is_percentage'])

    def test_is_percentage_with_non_percentage_rep_mode(self):

        self.query.add_series(self.field, rep_mode=constants.CHANGE)
        self.query.set_metadata_config(how=constants.METADATA_ONLY)
        meta = self.query.run()['meta']

        self.assertFalse(meta[1]['field']['is_percentage'])

    def test_add_query_aggregation(self):
        self.query.add_series(self.field)
        self.query.add_series(self.field, collapse_agg='sum')

        self.query.update_collapse('year')

        data = self.query.run()['data']
        for _, avg_value, sum_value in data:
            # Suma debe ser siempre mayor que el promedio
            self.assertGreater(sum_value, avg_value)

    def test_collapse_aggregation_series_order_different_periodicity(self):
        year_series = get_series_id('day')
        year_field = Field.objects.get(identifier=year_series)

        self.query.add_series(self.field, collapse_agg='sum')
        self.query.add_series(year_field)
        data = self.query.run()['data']

        other_query = Query()
        other_query.add_series(year_field)
        other_query.add_series(self.field, collapse_agg='sum')
        other_data = other_query.run()['data']

        for row1, row2 in zip(data, other_data):
            self.assertEqual(row1[0], row2[0])
            self.assertEqual(row1[1], row2[2])
            self.assertEqual(row1[2], row2[1])

    def test_add_two_collapses(self):
        """Esperado: El segundo collapse overridea el primero"""
        self.query.add_series(self.field)
        self.query.update_collapse('quarter')
        self.query.update_collapse('year')
        self.query.sort(how='asc')
        data = self.query.run()['data']

        prev_timestamp = None
        for row in data:
            timestamp = row[0]
            parsed_timestamp = iso8601.parse_date(timestamp)
            if not prev_timestamp:
                prev_timestamp = parsed_timestamp
                continue
            delta = relativedelta(parsed_timestamp, prev_timestamp)
            self.assertTrue(delta.years == 1, timestamp)
            prev_timestamp = parsed_timestamp

    def test_end_of_period_with_rep_mode(self):
        self.query.add_series(
            self.field,
            'percent_change',
            'end_of_period')
        self.query.update_collapse('year')
        self.query.sort('asc')
        data = self.query.run()['data']

        orig_eop = Query(index=settings.TS_INDEX)
        orig_eop.add_series(
            self.field,
            collapse_agg='end_of_period')
        orig_eop.update_collapse('year')
        orig_eop.sort('asc')
        end_of_period = orig_eop.run()['data']

        for i, row in enumerate(data):  # El primero es nulo en pct change
            value = end_of_period[i + 1][1] / end_of_period[i][1] - 1

            self.assertAlmostEqual(value, row[1])
