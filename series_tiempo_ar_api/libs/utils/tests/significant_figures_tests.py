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
        self.assertEqual(significant_figures([1.1, 1.2, 1.4]), 1)

    def test_figures_many_decimal_places(self):
        self.assertEqual(significant_figures([1.1, 1.24, 1.4, 5.3123]), 4)

    def test_figures_integer_and_decimals(self):
        self.assertEqual(significant_figures([1, 1.24, 20, 5.3123]), 4)
