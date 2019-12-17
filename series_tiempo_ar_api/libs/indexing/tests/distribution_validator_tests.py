#! coding: utf-8
import os
from mock import Mock, create_autospec

from django.test import TestCase
from series_tiempo_ar import TimeSeriesDataJson
from django_datajsonar.models import Distribution, Dataset

from series_tiempo_ar_api.libs.indexing.distribution_validator import DistributionValidator
from series_tiempo_ar_api.libs.indexing.errors.distribution_validator import DistributionValidationError
from series_tiempo_ar_api.libs.indexing.tests.reader_tests import SAMPLES_DIR


class DistributionValidatorTests(TestCase):
    def test_validator_valid_distribution_no_exceptions(self):
        catalog = TimeSeriesDataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        repository = self.create_mock_distribution_repository(catalog)
        validator = self.create_validator(repository)
        distribution = self.create_mock_distribution_from_first_catalog_entry(catalog)

        validator.run(distribution)

    def test_validate_distribution_without_dataset_identifier(self):
        catalog = TimeSeriesDataJson(os.path.join(SAMPLES_DIR, 'distribution_missing_dataset_identifier.json'))
        repository = self.create_mock_distribution_repository(catalog)
        validator = self.create_validator(repository)
        distribution = self.create_mock_distribution_from_first_catalog_entry(catalog)

        validator.run(distribution)

    def test_validate_distribution_multiple_errors(self):
        catalog = TimeSeriesDataJson(os.path.join(SAMPLES_DIR, 'repeated_field_id_and_description.json'))
        repository = self.create_mock_distribution_repository(catalog)

        distribution = self.create_mock_distribution_from_first_catalog_entry(catalog)
        validator = DistributionValidator(read_local=True,
                                          distribution_repository=repository)

        try:
            validator.run(distribution)
            msg = ''
        except DistributionValidationError as e:
            msg = str(e)
        self.assertIn('\n', msg)

    def create_mock_distribution_repository(self, distribution_catalog):
        repository = Mock()
        repository.return_value.get_data_json.return_value = distribution_catalog
        repository.return_value.get_index_time_series.return_value.title = 'indice_tiempo'
        return repository

    def create_mock_distribution_from_first_catalog_entry(self, catalog):
        # Accedo a los datos directamente, si uso catalog.get_distributions() hay side effects
        dataset = catalog['dataset'][0]
        distribution_data = dataset['distribution'][0]
        distribution = create_autospec(Distribution, spec_set=True,
                                       identifier=distribution_data['identifier'],
                                       download_url=distribution_data['downloadURL'],
                                       dataset=create_autospec(Dataset, identifier=dataset['identifier']))
        return distribution

    def create_validator(self, repository):
        data_validator = Mock()
        data_validator.validate.return_value = []
        validator = DistributionValidator(read_local=True,
                                          distribution_repository=repository,
                                          data_validator=data_validator)
        return validator
