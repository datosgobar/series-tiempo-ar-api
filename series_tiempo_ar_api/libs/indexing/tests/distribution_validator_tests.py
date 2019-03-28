#! coding: utf-8
import os

from django.test import TestCase
from mock import Mock
from pydatajson import DataJson

from series_tiempo_ar_api.libs.indexing.distribution_validator import DistributionValidator
from series_tiempo_ar_api.libs.indexing.tests.reader_tests import SAMPLES_DIR


class DistributionValidatorTests(TestCase):
    def test_validator_valid_distribution_no_exceptions(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        repository = self.create_mock_distribution_repository(catalog)
        validator = self.create_validator(repository)
        distribution = self.create_mock_distribution_from_first_catalog_entry(catalog)

        validator.run(distribution)

    def create_mock_distribution_repository(self, distribution_catalog):
        repository = Mock()
        repository.return_value.get_data_json.return_value = distribution_catalog
        repository.return_value.get_index_time_series.return_value.title = 'indice_tiempo'
        return repository

    def create_mock_distribution_from_first_catalog_entry(self, catalog):
        distribution_data = catalog.get_distributions(only_time_series=True)[0]
        distribution = Mock(identifier=distribution_data['identifier'], download_url=distribution_data['downloadURL'])
        return distribution

    def create_validator(self, repository):
        data_validator = Mock()
        validator = DistributionValidator(read_local=True,
                                          distribution_repository=repository,
                                          data_validator=data_validator)
        return validator
