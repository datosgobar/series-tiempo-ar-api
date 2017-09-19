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
            cmd().run(self.catalog)

    @staticmethod
    def init_commands():
        cmds = [
            DistributionScrapper
        ]
        return cmds


class DistributionScrapper:

    def __init__(self):
        self.distributions = []

    def run(self, catalog):
        datasets = catalog.pop('dataset', None)
        if not datasets:
            return

        title = catalog.pop('title', None)
        catalog_model = Catalog.objects.filter(title=title)
        if not catalog_model:
            catalog_model = Catalog(title=title)
        else:
            catalog_model = catalog_model[0]

        catalog_model.metadata = json.dumps(catalog)
        catalog_model.save()

        for dataset in datasets:
            distributions = dataset.pop('distribution', None)
            if not distributions:
                continue

            title = dataset.pop('title', None)
            dataset_model = Dataset.objects.filter(title=title)
            if not dataset_model:
                dataset_model = Dataset(title=title)
            else:
                dataset_model = dataset_model[0]
            dataset_model.metadata = json.dumps(dataset)
            dataset_model.catalog = catalog_model
            dataset_model.save()

            for distribution in distributions:
                fields = distribution.pop('field', None)

                if fields and fields[0]['specialType'] == 'time_index':
                    self.save(dataset_model, distribution, fields)

    def save(self, dataset_model, distribution, fields):
        title = distribution.pop('title', None)
        url = distribution.pop('downloadURL', None)
        if not url:
            return

        distribution_model = Distribution(metadata=json.dumps(distribution),
                                          title=title,
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
