#! coding: utf-8
import json

from .models import Catalog, Dataset, Distribution, Field


class ReaderPipeline:

    def __init__(self, catalog):
        self.args = {
            'catalog': catalog
        }
        self.catalog = None
        self.run()

    def run(self):
        scrapper = DistributionScrapper()
        scrapper.run(self.args)
        Validator().run(self.args)
        DatabaseLoader().run(self.args)


class DistributionScrapper:
    """Lee un catálogo y guarda las distribuciones de series de
    tiempo
    """
    def __init__(self):
        self.distributions = []

    def run(self, args):
        catalog = args['catalog']

        datasets = catalog.get('dataset', [])
        for dataset in datasets[:]:
            distributions = dataset.get('distribution', [])

            dataset_has_ts = False
            for distribution in distributions[:]:
                is_ts = self._distribution_check_if_time_series(distribution)
                if not is_ts:
                    distributions.remove(distribution)

                dataset_has_ts = True
            if not dataset_has_ts:
                datasets.remove(dataset)

        return catalog

    def _distribution_check_if_time_series(self, distribution):
        for field in distribution.get('field', []):
            if field.get('specialType') == 'time_index':
                self.distributions.append(distribution)
                return True

        return False


class DatabaseLoader:

    def run(self, args):
        catalog = args.get('catalog').copy()
        datasets = catalog.pop('dataset', None)

        catalog_model = self._catalog_model(catalog)
        for dataset in datasets:
            distributions = dataset.pop('distribution', None)

            dataset_model = self._dataset_model(catalog_model, dataset)
            for distribution in distributions:
                fields = distribution.pop('field', None)
                distribution_model = self._distribution_model(dataset_model,
                                                              distribution)
                self._save_fields(distribution_model, fields)

    @staticmethod
    def _dataset_model(catalog_model, dataset):
        title = dataset.pop('title', None)
        dataset_model, _ = Dataset.objects.get_or_create(
            title=title,
            catalog=catalog_model
        )
        dataset_model.metadata = json.dumps(dataset)
        dataset_model.save()
        return dataset_model

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

    @staticmethod
    def _distribution_model(dataset_model, distribution):
        title = distribution.pop('title', None)
        url = distribution.pop('downloadURL', None)

        distribution_model, _ = Distribution.objects.get_or_create(
            title=title,
            dataset=dataset_model
        )
        distribution_model.metadata = json.dumps(distribution)
        distribution_model.download_url = url
        distribution_model.save()
        return distribution_model

    @staticmethod
    def _save_fields(distribution_model, fields):
        for field in fields:
            if field.get('specialType') == 'time_index':
                continue

            series_id = field.pop('id')
            field_model, _ = Field.objects.get_or_create(
                series_id=series_id,
                distribution=distribution_model
            )
            field_model.metadata = json.dumps(field)
            field_model.save()


class Validator:

    def run(self, args):
        catalog = args.get('catalog', [])

        for dataset in catalog.get('dataset', []):
            distributions = dataset.get('distribution', [])
            for distribution in distributions[:]:
                if not self._validate_distribution(distribution):
                    distributions.remove(distribution)
                    continue

    def _validate_distribution(self, distribution):
        """Validaciones mínimas necesarias para que una distribución
        se estime como contenedora de series de tiempo. Devuelve un
        booleano dictando si se parseará su contenido o no
        """
        fields = distribution.get('field')
        time_index_found = False
        for field in fields[:]:
            if field.get('specialType') == 'time_index':
                if time_index_found:  # time_index duplicado!
                    return False

                periodicity = field.get('specialTypeDetail')
                if not self._validate_periodicity(periodicity):
                    return False
                time_index_found = True
        return True

    @staticmethod
    def _validate_periodicity(periodicity):
        if not periodicity:
            return False
        return True

    @staticmethod
    def _validate_fields(fields):
        for field in fields[:]:
            if field.get('type') not in ('number', 'integer'):
                fields.remove(field)
                # todo: logging de desestimación de un field
                continue
