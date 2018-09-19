import csv

from django.core.files import File
from iso8601 import iso8601

from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.generator.abstract_dump_gen import AbstractDumpGenerator
from series_tiempo_ar_api.apps.management import meta_keys


class SourcesCsvGenerator(AbstractDumpGenerator):

    columns = ['dataset_fuente', 'series_cant', 'valores_cant',
               'fecha_primer_valor', 'fecha_ultimo_valor']

    def generate(self, filepath):
        sources = {}

        for field in filter(lambda x: self.fields[x]['dataset_fuente'], self.fields):
            source = self.fields[field]['dataset_fuente']
            field_model: Field = self.fields[field]['serie']

            if source not in sources:
                sources[source] = {
                    self.columns[0]: source,
                    self.columns[1]: 0,
                    self.columns[2]: 0,
                    self.columns[3]: None,
                    self.columns[4]: None,
                }

            sources[source]['series_cant'] += 1
            index_start = iso8601.parse_date(meta_keys.get(field_model, meta_keys.INDEX_START)).date()
            index_end = iso8601.parse_date(meta_keys.get(field_model, meta_keys.INDEX_END)).date()
            index_size = int(meta_keys.get(field_model, meta_keys.INDEX_SIZE))

            if sources[source]['fecha_primer_valor'] is None or sources[source]['fecha_primer_valor'] > index_start:
                sources[source]['fecha_primer_valor'] = index_start

            if sources[source]['fecha_ultimo_valor'] is None or sources[source]['fecha_ultimo_valor'] < index_end:
                sources[source]['fecha_ultimo_valor'] = index_end

            sources[source]['valores_cant'] += index_size

        self.write(filepath, sources)

    def write(self, filepath: str, sources: dict):
        with open(filepath, 'w') as f:
            writer = csv.DictWriter(f, self.columns)
            writer.writeheader()
            writer.writerows(sources.values())

        with open(filepath, 'rb') as f:
            self.task.dumpfile_set.create(file_name=constants.SOURCES_CSV, file=File(f))
