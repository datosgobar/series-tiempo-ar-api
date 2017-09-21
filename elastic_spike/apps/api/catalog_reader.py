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
        for dataset in datasets:
            distributions = dataset.pop('distribution', None)
            if not distributions:
                continue

            title = dataset.pop('title', None)
            dataset_model, _ = Dataset.objects.get_or_create(
                title=title,
                catalog=catalog_model
            )
            dataset_model.metadata = json.dumps(dataset)
            dataset_model.save()
            for distribution in distributions:
                fields = distribution.pop('field', None)

                if fields and fields[0]['specialType'] == 'time_index':
                    self.save(dataset_model, distribution, fields)

    @staticmethod
    def _catalog_model(catalog):
        """Crea o actualiza el catalog model con el título pedido a partir
        de el diccionario de metadatos de un catálogo
        """
        title = catalog.pop('title', None)
        catalog_model, _ = Catalog.objects.get_or_create(title=title)
        catalog_model.metadata = json.dumps(catalog)
        catalog_model.save()
        return catalog_model

    def save(self, dataset_model, distribution, fields):
        title = distribution.pop('title', None)
        url = distribution.pop('downloadURL', None)
        if not url:
            return

        distribution_model, _ = Distribution.objects.get_or_create(
            title=title,
            dataset=dataset_model
        )
        distribution_model.metadata = json.dumps(distribution)
        distribution_model.save()

        self.distributions.append(distribution_model)
        for field in fields:
            series_id = field.pop('id')
            field_model, _ = Field.objects.get_or_create(
                series_id=series_id,
                distribution=distribution_model
            )
            field_model.metadata = json.dumps(field)

            self.fields.append(field_model)
