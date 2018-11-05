import csv
from iso8601 import iso8601

from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.dump.generator.abstract_dump_gen import AbstractDumpGenerator
from series_tiempo_ar_api.apps.dump.generator import constants
from series_tiempo_ar_api.apps.dump.models import DumpFile
from series_tiempo_ar_api.apps.management import meta_keys


class SourcesCsvGenerator(AbstractDumpGenerator):
    filename = DumpFile.FILENAME_SOURCES
    columns = constants.SOURCES_ROWS

    def generate(self):
        sources = {}

        for field in filter(lambda x: self.fields[x]['dataset_fuente'], self.fields):
            source = self.fields[field]['dataset_fuente']
            field_model: Field = self.fields[field]['serie']

            if source not in sources:
                sources[source] = {
                    constants.SOURCES_DATASET_SOURCE: source,
                    constants.SOURCE_SERIES_AMT: 0,
                    constants.SOURCE_VALUES_AMT: 0,
                    constants.SOURCE_FIRST_INDEX: None,
                    constants.SOURCE_LAST_INDEX: None,
                }

            sources[source][constants.SOURCE_SERIES_AMT] += 1
            index_start = meta_keys.get(field_model, meta_keys.INDEX_START)

            # ☢☢☢
            if index_start:
                index_start = iso8601.parse_date(index_start).date()
                first_index = sources[source][constants.SOURCE_FIRST_INDEX]
                if first_index is None or first_index > index_start:
                    sources[source][constants.SOURCE_FIRST_INDEX] = index_start

            index_end = meta_keys.get(field_model, meta_keys.INDEX_END)
            if index_end:
                index_end = iso8601.parse_date(index_end).date()
                last_index = sources[source][constants.SOURCE_LAST_INDEX]
                if last_index is None or last_index < index_end:
                    sources[source][constants.SOURCE_LAST_INDEX] = index_end

            index_size = meta_keys.get(field_model, meta_keys.INDEX_SIZE) or 0

            if index_size:
                index_size = int(index_size)

            sources[source][constants.SOURCE_VALUES_AMT] += index_size

        self.write_tmp_file(sources)

    def write_tmp_file(self, sources: dict):
        filepath = self.get_file_path()
        rows = sorted(sources.values(), key=lambda source: source[constants.SOURCE_SERIES_AMT], reverse=True)
        with open(filepath, 'w') as f:
            writer = csv.DictWriter(f, self.columns)
            writer.writeheader()
            writer.writerows(rows)

        self.write(filepath, self.filename)
