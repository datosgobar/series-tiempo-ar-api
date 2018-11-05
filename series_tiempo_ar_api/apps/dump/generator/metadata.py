import csv
from series_tiempo_ar_api.apps.dump.generator.abstract_dump_gen import AbstractDumpGenerator
from series_tiempo_ar_api.apps.dump.models import DumpFile
from series_tiempo_ar_api.apps.management import meta_keys
from . import constants


class MetadataCsvGenerator(AbstractDumpGenerator):
    filename = DumpFile.FILENAME_METADATA
    rows = constants.METADATA_ROWS

    def generate(self):
        filepath = self.get_file_path()
        with open(filepath, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.rows)

            writer.writeheader()
            for field, values in self.fields.items():
                writer.writerow(self.generate_row(field, values))

        self.write(filepath, self.filename)

    def generate_row(self, serie_name, values):
        dataset = values['dataset']
        distribution = values['distribution']
        serie = values['serie']

        return {
            constants.CATALOG_ID: dataset.catalog.identifier,
            constants.DATASET_ID: dataset.identifier,
            constants.DISTRIBUTION_ID: distribution.identifier,
            constants.SERIE_ID: serie_name,
            constants.TIME_INDEX_FREQUENCY: meta_keys.get(distribution, meta_keys.PERIODICITY),
            constants.SERIES_TITLE: values[constants.SERIES_TITLE],
            constants.SERIES_UNITS: values[constants.SERIES_UNITS],
            constants.SERIES_DESCRIPTION: values[constants.SERIES_DESCRIPTION],
            constants.DISTRIBUTION_TITLE: values[constants.DISTRIBUTION_TITLE],
            constants.DISTRIBUTION_DESCRIPTION: values[constants.DATASET_PUBLISHER],
            constants.DISTRIBUTION_DOWNLOAD_URL: values[constants.DISTRIBUTION_DOWNLOAD_URL],
            constants.DATASET_PUBLISHER: values[constants.DATASET_TITLE],
            constants.DATASET_SOURCE: values[constants.DATASET_SOURCE],
            constants.DATASET_TITLE: values[constants.DATASET_TITLE],
            constants.DATASET_DESCRIPTION: values[constants.DATASET_DESCRIPTION],
            constants.DATASET_THEME: values[constants.DATASET_THEME],
            constants.SERIES_INDEX_START: meta_keys.get(serie, meta_keys.INDEX_START),
            constants.SERIES_INDEX_END: meta_keys.get(serie, meta_keys.INDEX_END),
            constants.SERIES_VALUES_AMT: meta_keys.get(serie, meta_keys.INDEX_SIZE),
            constants.SERIES_DAYS_SINCE_LAST_UPDATE: meta_keys.get(serie, meta_keys.DAYS_SINCE_LAST_UPDATE),
            constants.SERIES_IS_UPDATED: meta_keys.get(serie, meta_keys.IS_UPDATED),
            constants.SERIES_LAST_VALUE: meta_keys.get(serie, meta_keys.LAST_VALUE),
            constants.SERIES_SECOND_LAST_VALUE: meta_keys.get(serie, meta_keys.SECOND_TO_LAST_VALUE),
            constants.SERIES_PCT_CHANGE: meta_keys.get(serie, meta_keys.LAST_PCT_CHANGE),
        }
