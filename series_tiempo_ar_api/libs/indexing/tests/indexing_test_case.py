from django.test import TestCase, override_settings


@override_settings(TS_INDEX='indexing_test_case_indicators')
class IndexingTestCase(TestCase):
    pass
