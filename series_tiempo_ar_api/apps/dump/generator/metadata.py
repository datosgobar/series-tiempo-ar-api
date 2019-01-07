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
            for field in self.ordered_fields():
                values = self.fields[field]
                writer.writerow(self.generate_row(field, values))

        self.write(filepath, self.filename)

    def ordered_fields(self):
        return sorted(self.fields,
                      key=self.row_order)

    def row_order(self, field: str):
        field_data = self.fields[field]
        return (
            field_data['dataset'].catalog.identifier,
            field_data['dataset'].identifier,
            field_data['distribution'].identifier,
            field,
            field_data[meta_keys.PERIODICITY],
        )

    def generate_row(self, serie_name, values):
        dataset = values['dataset']
        distribution = values['distribution']

        return {
            constants.CATALOG_ID: dataset.catalog.identifier,
            constants.DATASET_ID: dataset.identifier,
            constants.DISTRIBUTION_ID: distribution.identifier,
            constants.SERIE_ID: serie_name,
            constants.TIME_INDEX_FREQUENCY: values[meta_keys.PERIODICITY],
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
            constants.SERIES_INDEX_START: values['metadata'].get(meta_keys.INDEX_START),
            constants.SERIES_INDEX_END: values['metadata'].get(meta_keys.INDEX_END),
            constants.SERIES_VALUES_AMT: values['metadata'].get(meta_keys.INDEX_SIZE),
            constants.SERIES_DAYS_SINCE_LAST_UPDATE: values['metadata'].get(meta_keys.DAYS_SINCE_LAST_UPDATE),
            constants.SERIES_IS_UPDATED: values['metadata'].get(meta_keys.IS_UPDATED),
            constants.SERIES_LAST_VALUE: values['metadata'].get(meta_keys.LAST_VALUE),
            constants.SERIES_SECOND_LAST_VALUE: values['metadata'].get(meta_keys.SECOND_TO_LAST_VALUE),
            constants.SERIES_PCT_CHANGE: values['metadata'].get(meta_keys.LAST_PCT_CHANGE),
        }
