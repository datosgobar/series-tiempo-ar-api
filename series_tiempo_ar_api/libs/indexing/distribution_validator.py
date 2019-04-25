#! coding: utf-8

from series_tiempo_ar.validations import validate_distribution
from django_datajsonar.models import Distribution

from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository


class DistributionValidator(object):
    def __init__(self,
                 read_local=False,
                 distribution_repository=DistributionRepository,
                 data_validator=validate_distribution):
        self.read_local = read_local
        self.distribution_repository = distribution_repository
        self.data_validator = data_validator

    def run(self, distribution_model: Distribution):
        """Lanza excepciones si la distribución no es válida"""
        df = self.distribution_repository(distribution_model).read_csv_as_time_series_dataframe()

        catalog = self.distribution_repository(distribution_model).get_data_json()
        distribution = catalog.get_distribution(distribution_model.identifier)
        dataset = catalog.get_dataset(distribution_model.dataset.identifier)

        self.data_validator(df, catalog, dataset, distribution)
