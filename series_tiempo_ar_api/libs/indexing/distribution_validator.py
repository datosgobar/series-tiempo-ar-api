#! coding: utf-8

from series_tiempo_ar.validations import get_distribution_errors, ValidationOptions
from django_datajsonar.models import Distribution

from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.indexing.errors.distribution_validator import DistributionValidationError


class DataValidator:

    def __init__(self, validator_function, options=None):
        self.validator_function = validator_function
        self.options = options

    def validate(self, catalog, distribution_id):
        return self.validator_function(catalog, distribution_id, options=self.options)


class DistributionValidator:
    def __init__(self,
                 read_local=False,
                 distribution_repository=DistributionRepository,
                 data_validator=DataValidator(get_distribution_errors)):
        self.read_local = read_local
        self.distribution_repository = distribution_repository
        self.data_validator = data_validator

    def run(self, distribution_model: Distribution):
        """Lanza excepciones si la distribución no es válida"""

        catalog = self.distribution_repository(distribution_model).get_data_json()

        errors = self.data_validator.validate(catalog, distribution_model.identifier)
        if errors:
            raise DistributionValidationError('\n\n'.join([str(e) for e in errors]))
