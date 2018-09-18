import csv

from django.core.files import File
from iso8601 import iso8601

from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.dump import constants
from series_tiempo_ar_api.apps.dump.generator.abstract_dump_gen import AbstractDumpGenerator
from series_tiempo_ar_api.apps.management import meta_keys


class SourcesCsvGenerator(AbstractDumpGenerator):

    def generate(self, filepath):
        sources = {}

        for field in self.fields:
            source = self.fields[field]['dataset_fuente']
            field_model: Field = self.fields[field]['serie']

            if source not in sources:
                sources[source] = {
                    'dataset_fuente': source,
                    'series_cant': 0,
                    'valores_cant': 0,
                    'fecha_primer_valor': None,
                    'fecha_ultimo_valor': None,
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
            values = list(sources.values())
            writer = csv.DictWriter(f, values[0].keys())
            writer.writeheader()
            writer.writerows(values)

        with open(filepath, 'rb') as f:
            self.task.dumpfile_set.create(file_name=constants.SOURCES_CSV, file=File(f))
