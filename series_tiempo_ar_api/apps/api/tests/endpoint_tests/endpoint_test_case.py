from django.test import Client
from django.urls import reverse

from series_tiempo_ar_api.apps.api.tests.helpers import get_series_id, get_delayed_series_id


class EndpointTestCase:
    """
    Clase base para tests de endpoint con varios valores útiles ya seteados

    Los datos se encuentran presentes en el índice de pruebas,
    generado bajo tests/support/generate_data.csv (y "cacheado" bajo data.csv)

    Las series generadas son:
        - Series de todas las frecuencias, desde el 1999 hasta el 2009, con su
        primer dato en 1999-01-01 == 100, y luego aumentando en 1 por cada período
        - Series de todas las frecuencias, desde el 2004 hasta el 2014, con su
        primer dato en 2004-01-01 == 100, y luego aumentando en 1 por cada período
    """

    def __init__(self, *args, **kwargs):
        self.client = Client()
        self._monotonic_increasing_series()
        self._monotonic_increasing_delayed_series()

    def _monotonic_increasing_series(self):
        self.increasing_day_series_id = get_series_id('day')
        self.increasing_month_series_id = get_series_id('month')
        self.increasing_quarter_series_id = get_series_id('quarter')
        self.increasing_year_series_id = get_series_id('year')

    def _monotonic_increasing_delayed_series(self):
        self.increasing_day_series_id_2004 = get_delayed_series_id('day')
        self.increasing_month_series_id_2004 = get_delayed_series_id('month')
        self.increasing_quarter_series_id_2004 = get_delayed_series_id('quarter')
        self.increasing_year_series_id_2004 = get_delayed_series_id('year')

    def run_query(self, data):
        return self.client.get(reverse('api:series:series'), data=data).json()
