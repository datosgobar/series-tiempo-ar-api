import numpy as np
from django.test import SimpleTestCase

from series_tiempo_ar_api.libs.utils.significant_figures import significant_figures


class SignificantFiguresTests(SimpleTestCase):

    def test_figures_empty_list(self):
        self.assertEqual(significant_figures([]), 0)

    def test_figures_single_element_without_figures(self):
        self.assertEqual(significant_figures([1]), 0)

    def test_figures_all_integers(self):
        self.assertEqual(significant_figures([1, 2, 302, 20, 15]), 0)

    def test_figures_all_single_point_decimal(self):
        self.assertEqual(significant_figures([1.1, 1.20, 1.400]), 1)

    def test_figures_many_decimal_places(self):
        self.assertEqual(significant_figures([1.1, 1.24, 1.4, 5.3123]), 4)

    def test_figures_integer_and_decimals(self):
        self.assertEqual(significant_figures([1, 1.24, 20, 5.3123]), 4)

    def test_figures_nan_ignored(self):
        self.assertEqual(significant_figures([1, np.nan, 1.24, 20, 5.3123]), 4)

    def test_point_zero_floats(self):
        self.assertEqual(significant_figures([1.0, np.nan, 10.00, 20, 2.0]), 0)

    def test_float_error(self):
        zero_point_three = 0.1 + 0.2  # https://0.30000000000000004.com/
        self.assertEqual(significant_figures([zero_point_three]), 1)
