import csv
from iso8601 import iso8601

from django_datajsonar.models import Field

from series_tiempo_ar_api.apps.dump.generator.abstract_dump_gen import AbstractDumpGenerator
from series_tiempo_ar_api.apps.dump.models import DumpFile
from series_tiempo_ar_api.apps.management import meta_keys


class SourcesCsvGenerator(AbstractDumpGenerator):
    filename = DumpFile.FILENAME_SOURCES
    columns = ['dataset_fuente', 'series_cant', 'valores_cant',
               'fecha_primer_valor', 'fecha_ultimo_valor']

    def generate(self):
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
            index_start = meta_keys.get(field_model, meta_keys.INDEX_START)

            # ☢☢☢
            if index_start:
                index_start = iso8601.parse_date(index_start).date()
                if sources[source]['fecha_primer_valor'] is None or sources[source]['fecha_primer_valor'] > index_start:
                    sources[source]['fecha_primer_valor'] = index_start

            index_end = meta_keys.get(field_model, meta_keys.INDEX_END)
            if index_end:
                index_end = iso8601.parse_date(index_end).date()
                if sources[source]['fecha_ultimo_valor'] is None or sources[source]['fecha_ultimo_valor'] < index_end:
                    sources[source]['fecha_ultimo_valor'] = index_end

            index_size = meta_keys.get(field_model, meta_keys.INDEX_SIZE) or 0

            if index_size:
                index_size = int(index_size)

            sources[source]['valores_cant'] += index_size

        self.write_tmp_file(sources)

    def write_tmp_file(self, sources: dict):
        filepath = self.get_file_path()
        with open(filepath, 'w') as f:
            writer = csv.DictWriter(f, self.columns)
            writer.writeheader()
            writer.writerows(sources.values())

        self.write(filepath, self.filename)
