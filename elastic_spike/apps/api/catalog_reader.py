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
        self.fields = []

    def run(self, catalog):
        datasets = catalog.pop('dataset', None)
        if not datasets:
            return

        catalog_model = self._catalog_model(catalog)
        dataset_models = []
        for dataset in datasets:
            distributions = dataset.pop('distribution', None)
            if not distributions:
                continue

            title = dataset.pop('title', None)
            dataset_model = Dataset.objects.filter(title=title)
            if not dataset_model:
                dataset_model = Dataset(title=title)
                dataset_models.append(dataset_model)
            else:
                dataset_model = dataset_model[0]
            dataset_model.metadata = json.dumps(dataset)
            dataset_model.catalog = catalog_model

            for distribution in distributions:
                fields = distribution.pop('field', None)

                if fields and fields[0]['specialType'] == 'time_index':
                    self.save(dataset_model, distribution, fields)

        Dataset.objects.bulk_create(dataset_models)
        Distribution.objects.bulk_create(self.distributions)
        Field.objects.bulk_create(self.fields)

    @staticmethod
    def _catalog_model(catalog):
        title = catalog.pop('title', None)
        catalog_model = Catalog.objects.filter(title=title)
        if not catalog_model:
            catalog_model = Catalog(title=title)
        else:
            catalog_model = catalog_model[0]
        catalog_model.metadata = json.dumps(catalog)
        catalog_model.save()
        return catalog_model

    def save(self, dataset_model, distribution, fields):
        title = distribution.pop('title', None)
        url = distribution.pop('downloadURL', None)
        if not url:
            return

        distribution_model = Distribution(metadata=json.dumps(distribution),
                                          title=title,
                                          dataset=dataset_model,
                                          download_url=url)
        self.distributions.append(distribution_model)
        for field in fields:
            series_id = field.pop('id')
            field = Field(metadata=json.dumps(field),
                          distribution=distribution_model,
                          series_id=series_id)
            self.fields.append(field)
