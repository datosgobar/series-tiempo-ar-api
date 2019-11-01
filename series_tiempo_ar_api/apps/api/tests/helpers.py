#! coding: utf-8

from django.conf import settings
from django_datajsonar.models import Catalog

from series_tiempo_ar_api.apps.management import meta_keys


def setup_database():
    """Crea todos los modelos necesarios para las series de test, creadas a través
    del generador en support/generate_data.py

    Todas las series pertenecen al mismo Catálogo y Dataset, va variando la distribución
    según la frecuencia de las series.
    """
    DatabaseLoader('test_catalog', '132').init_data()


class DatabaseLoader:

    def __init__(self, catalog_title, dataset_id):
        self.catalog_id = catalog_title
        self.dataset_id = dataset_id

        self.dataset = None

    def init_data(self):
        catalog = Catalog.objects.create(title=self.catalog_id, metadata='{}')
        self.dataset = catalog.dataset_set.create(identifier=self.dataset_id,
                                                  metadata='{}',
                                                  catalog=catalog)

        self._increasing_series()
        self._increasing_series_delayed()

    def _increasing_series(self):
        start_date = '1999-01-01'
        year = self._create_distribution('R/P1Y')
        self._create_field(year, get_series_id('year'), 'random_year_0_title', start_date)
        semester = self._create_distribution('R/P6M')
        self._create_field(semester, get_series_id('semester'), 'random_semester_0_title', start_date)
        month = self._create_distribution('R/P1M')
        self._create_field(month, get_series_id('month'), 'random_month_0_title', start_date)
        day = self._create_distribution('R/P1D')
        self._create_field(day, get_series_id('day'), 'random_day_0_title', start_date)

    def _create_distribution(self, periodicity):
        count = self.dataset.distribution_set.count()
        identifier = f'{self.dataset_id}.{count + 1}'
        distrib = self.dataset.distribution_set.create(identifier=identifier,
                                                       metadata='{}',
                                                       download_url="invalid_url")
        distrib.enhanced_meta.create(key=meta_keys.PERIODICITY, value=periodicity)
        return distrib

    def _create_field(self, distribution, identifier, title, index_start):
        field = distribution.field_set.create(
            identifier=identifier,
            metadata='{"description": "test_series_description", "units": "percentage"}',
            distribution=distribution,
            title=title
        )
        field.enhanced_meta.create(key=meta_keys.AVAILABLE, value='True')
        field.enhanced_meta.create(key=meta_keys.PERIODICITY,
                                   value=meta_keys.get(distribution, meta_keys.PERIODICITY))
        field.enhanced_meta.create(key=meta_keys.INDEX_START, value=index_start)

    def _increasing_series_delayed(self):
        start_date = '2004-01-01'
        year = self._create_distribution('R/P1Y')
        self._create_field(year, get_delayed_series_id('year'), 'random_year_0_title_delayed', start_date)
        semester = self._create_distribution('R/P6M')
        self._create_field(semester, get_delayed_series_id('semester'), 'random_semester_0_title_delayed', start_date)
        month = self._create_distribution('R/P1M')
        self._create_field(month, get_delayed_series_id('month'), 'random_month_0_title_delayed', start_date)
        day = self._create_distribution('R/P1D')
        self._create_field(day, get_delayed_series_id('day'), 'random_day_0_title_delayed', start_date)


def get_series_id(periodicity):
    return settings.TEST_SERIES_NAME.format(periodicity)


def get_delayed_series_id(periodicity):
    return settings.TEST_SERIES_NAME_DELAYED.format(periodicity)
