#! coding: utf-8

from django.conf import settings
from series_tiempo_ar_api.apps.api.models import \
    Catalog, Dataset, Distribution, Field


def setup_database():
    if Catalog.objects.count():  # Garantiza que solo corra una vez
        return

    catalog = Catalog.objects.create(title='test_catalog', metadata='{}')
    dataset = Dataset.objects.create(identifier="132",
                                     metadata='{}',
                                     catalog=catalog)
    init_year_series(dataset)
    init_semester_series(dataset)
    init_month_series(dataset)
    init_daily_series(dataset)


def init_year_series(dataset):
    distrib = Distribution.objects.create(identifier='132.1',
                                          metadata='{}',
                                          download_url="invalid_url",
                                          dataset=dataset,
                                          periodicity='R/P1Y')
    Field.objects.create(
        series_id=settings.TEST_SERIES_NAME.format('year'),
        metadata='{}',
        distribution=distrib,
        description="random series description",
        title='random_year_0_title'
    )


def init_semester_series(dataset):
    distrib = Distribution.objects.create(identifier='132.2',
                                          metadata='{}',
                                          download_url="invalid_url",
                                          dataset=dataset,
                                          periodicity='R/P6M')
    Field.objects.create(
        series_id=settings.TEST_SERIES_NAME.format('semester'),
        metadata='{}',
        distribution=distrib,
        title='random_semester_0_title'
    )


def init_month_series(dataset):

    distrib = Distribution.objects.create(identifier='132.3',
                                          metadata='{}',
                                          download_url="invalid_url",
                                          dataset=dataset,
                                          periodicity='R/P1M')
    Field.objects.create(
        series_id=settings.TEST_SERIES_NAME.format('month'),
        metadata='{}',
        distribution=distrib,
        description="random series description",
        title='random_month_0_title'
    )
    return dataset


def init_daily_series(dataset):
    distrib = Distribution.objects.create(identifier='132.4',
                                          metadata='{}',
                                          download_url="invalid_url",
                                          dataset=dataset,
                                          periodicity='R/P1D')
    Field.objects.create(
        series_id=settings.TEST_SERIES_NAME.format('day'),
        metadata='{}',
        distribution=distrib,
        title='random_day_0_title'
    )


def get_series_id(periodicity):
    return settings.TEST_SERIES_NAME.format(periodicity)
