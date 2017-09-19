#! coding: utf-8
import json


from .models import Catalog, Dataset, Distribution, Field


class ReaderPipeline:

    def __init__(self, catalog):
        self.catalog = catalog
        self.commands = self.init_commands()
        self.run()

    def run(self):
        for cmd in self.commands:
            cmd.run(self.catalog)

    @staticmethod
    def init_commands():
        cmds = []
        return cmds


class DistributionScrapper:

    def __init__(self):
        self.distributions = []

    def run(self, catalog):
        datasets = catalog.get('dataset')

        for dataset in datasets:
            distributions = dataset.get('distribution')

            for distribution in distributions:
                fields = distribution.get('field')
                if fields and fields[0]['specialType'] == 'time_index':
                    self.save(catalog, dataset, distribution, fields)

    def save(self, catalog, dataset, distribution, fields):
        catalog.pop('dataset', None)
        catalog_model = Catalog(metadata=json.dumps(catalog))
        catalog_model.save()

        dataset.pop('distribution', None)
        dataset_model = Dataset(metadata=json.dumps(dataset),
                                catalog=catalog_model)
        dataset_model.save()

        distribution.pop('field')
        url = distribution.pop('downloadUrl')
        distribution_model = Distribution(metadata=json.dumps(distribution),
                                          dataset=dataset_model,
                                          download_url=url)
        distribution_model.save()
        self.distributions.append(distribution)
        for field in fields:
            series_id = field.pop('id')
            field = Field(metadata=json.dumps(field),
                          distribution=distribution_model,
                          series_id=series_id)
            field.save()
