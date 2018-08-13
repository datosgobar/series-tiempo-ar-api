#! coding: utf-8
import iso8601
from django.conf import settings
from django.test import TestCase
from nose.tools import raises

from series_tiempo_ar_api.apps.management import meta_keys
from series_tiempo_ar_api.apps.api.exceptions import CollapseError
from django_datajsonar.models import Field
from series_tiempo_ar_api.apps.api.query.query import Query
from .helpers import get_series_id

SERIES_NAME = get_series_id('month')


class QueryTests(TestCase):
    single_series = SERIES_NAME

    @classmethod
    def setUpClass(cls):
        cls.field = Field.objects.get(identifier=cls.single_series)
        super(cls, QueryTests).setUpClass()

    def setUp(self):
        self.query = Query(index=settings.TEST_INDEX)

    def test_index_metadata_frequency(self):
        self.query.add_series(self.single_series, self.field)
        self.query.run()

        index_frequency = self.query.get_metadata()[0]['frequency']
        self.assertEqual(index_frequency, 'month')

    def test_index_metadata_start_end_dates(self):
        self.query.add_series(self.single_series, self.field)
        data = self.query.run()['data']

        index_meta = self.query.get_metadata()[0]
        self.assertEqual(data[0][0], index_meta['start_date'])
        self.assertEqual(data[-1][0], index_meta['end_date'])

    def test_collapse_index_metadata_frequency(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse(collapse=collapse_interval)
        self.query.run()

        index_frequency = self.query.get_metadata()[0]['frequency']
        self.assertEqual(index_frequency, collapse_interval)

    def test_collapse_index_metadata_start_end_dates(self):
        collapse_interval = 'quarter'
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse(collapse=collapse_interval)
        data = self.query.run()['data']

        index_meta = self.query.get_metadata()[0]
        self.assertEqual(data[0][0], index_meta['start_date'])
        self.assertEqual(data[-1][0], index_meta['end_date'])

    @raises(CollapseError)
    def test_invalid_collapse(self):
        collapse_interval = 'day'  # Serie cargada es mensual
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse(collapse=collapse_interval)

    def test_identifiers(self):

        self.query.add_series(self.single_series, self.field)
        # Devuelve lista de ids, una por serie. Me quedo con la primera (única)
        ids = self.query.get_series_identifiers()[0]
        field = Field.objects.get(identifier=self.single_series)
        self.assertEqual(ids['id'], field.identifier)
        self.assertEqual(ids['distribution'], field.distribution.identifier)
        self.assertEqual(ids['dataset'], field.distribution.dataset.identifier)

    def test_weekly_collapse(self):
        day_series_name = settings.TEST_SERIES_NAME.format('day')
        field = Field.objects.get(identifier=day_series_name)

        self.query.add_series(day_series_name, field)

        self.query.add_collapse(collapse='week')
        self.query.sort(how='asc')
        data = self.query.run()['data']

        first_date = iso8601.parse_date(data[0][0])
        second_date = iso8601.parse_date(data[1][0])

        delta = second_date - first_date
        self.assertEqual(delta.days, 7)

    def add_series_with_aggregation(self):
        # Aggregation sin haber definido collapse NO HACE NADA!
        self.query.add_series(self.single_series, self.field, collapse_agg='sum')
        self.assertTrue(self.query.series_models)

    def test_simple_metadata_remove_catalog(self):
        catalog = self.field.distribution.dataset.catalog
        catalog.metadata = '{"title": "test_title", "extra_field": "extra"}'
        catalog.save()

        self.query.add_series(self.single_series, self.field)
        self.query.run()
        index_meta = self.query.get_metadata()[1]['catalog']
        self.assertNotIn('extra_field', index_meta)
        self.assertIn('title', index_meta)

    def test_simple_metadata_remove_dataset(self):
        dataset = self.field.distribution.dataset
        dataset.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dataset.save()

        self.query.add_series(self.single_series, self.field)
        self.query.run()
        index_meta = self.query.get_metadata()[1]['dataset']
        self.assertNotIn('extra_field', index_meta)
        self.assertIn('title', index_meta)

    def test_simple_metadata_remove_distribution(self):
        dist = self.field.distribution
        dist.metadata = '{"title": "test_title", "extra_field": "extra"}'
        dist.save()

        self.query.add_series(self.single_series, self.field)
        self.query.run()
        index_meta = self.query.get_metadata()[1]['distribution']
        self.assertNotIn('extra_field', index_meta)
        self.assertIn('title', index_meta)

    def test_simple_metadata_remove_field(self):
        self.field.metadata = '{"id": "test_title", "extra_field": "extra"}'
        self.field.save()

        self.query.add_series(self.single_series, self.field)
        self.query.run()
        index_meta = self.query.get_metadata()[1]['field']
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
        self.field.save()

        self.query.add_series(self.single_series, self.field)
        self.query.flatten_metadata_response()
        self.query.run()

        flat_meta = self.query.get_metadata()[1]

        other_query = Query(index=settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.field)
        other_query.run()
        meta = other_query.get_metadata()[1]

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
        self.field.save()

        self.query.add_series(self.single_series, self.field)
        self.query.set_metadata_config('full')
        self.query.flatten_metadata_response()
        self.query.run()

        flat_meta = self.query.get_metadata()[1]

        other_query = Query(index=settings.TEST_INDEX)
        other_query.add_series(self.single_series, self.field)
        other_query.set_metadata_config('full')
        other_query.run()
        meta = other_query.get_metadata()[1]

        for key in meta:
            for in_key in meta[key]:
                self.assertEqual(meta[key][in_key], flat_meta['{}_{}'.format(key, in_key)])

    def test_full_metadata_includes_enhanced_meta(self):
        self.query.add_series(self.single_series, self.field)
        self.query.set_metadata_config('full')
        meta = self.query.get_metadata()

        for enhanced_meta in self.field.enhanced_meta.all():
            self.assertEqual(meta[1]['field'][enhanced_meta.key], enhanced_meta.value)

    def test_full_metadata_periodicty_with_collapse(self):
        self.query.add_series(self.single_series, self.field)
        self.query.add_collapse('year')
        self.query.set_metadata_config('full')

        resp = self.query.run()

        self.assertEqual(resp['meta'][0]['frequency'], 'year')
        self.assertEqual(resp['meta'][1]['field'][meta_keys.PERIODICITY],
                         meta_keys.get(self.field, meta_keys.PERIODICITY))

    def test_query_count(self):
        self.query.add_series(self.single_series, self.field)

        resp = self.query.run()

        # Longitud de la serie pedida. Ver support/generate_data.py
        self.assertEqual(resp['count'], 1000)

    def test_day_series_length_with_limit_and_rep_mode(self):
        day_series_name = settings.TEST_SERIES_NAME.format('day')
        field = Field.objects.get(identifier=day_series_name)

        self.query.add_series(day_series_name, field, rep_mode='percent_change_a_year_ago')
        self.query.add_pagination(start=0, limit=2)
        result = self.query.run()

        self.assertEqual(len(result['data']), 2)
