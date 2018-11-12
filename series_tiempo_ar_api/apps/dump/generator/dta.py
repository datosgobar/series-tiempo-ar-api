import os

import pandas as pd
import numpy as np
from django.core.files import File
from django_datajsonar.models import Node

from series_tiempo_ar_api.apps.dump.models import DumpFile, GenerateDumpTask


class DtaGenerator:

    def __init__(self, task_id: int, catalog_id: str = None):
        self.task = GenerateDumpTask.objects.get(id=task_id)
        self.node = Node.objects.get(catalog_id=catalog_id) if catalog_id else None

    def generate(self):
        dumps = [DumpFile.FILENAME_METADATA, DumpFile.FILENAME_SOURCES, DumpFile.FILENAME_VALUES]
        for dump in dumps:
            self.generate_dump(dump)

    def generate_dump(self, dump_name):
        dump_file = DumpFile.objects.filter(file_type=DumpFile.TYPE_CSV,
                                            file_name=dump_name,
                                            node=self.node).last()
        df = pd.read_csv(dump_file.file)
        if dump_file.file_name == DumpFile.FILENAME_VALUES:
            df = df[['serie_id', 'indice_tiempo', 'valor']]

        with FileWrapper(self.file_name(dump_file)) as f:
            save_to_dta(df, f.filepath)
            self.task.dumpfile_set.create(file_type=DumpFile.TYPE_DTA,
                                          file_name=dump_name,
                                          node=dump_file.node,
                                          file=File(open(f.filepath, 'rb')))

    def file_name(self, dump_file: DumpFile):
        return f'{dump_file.node}-{dump_file.file_name}-{dump_file.id}.dta'


def save_to_dta(df, path, str_limit=244):
    df_stata = df.copy()
    for col in df_stata.columns:

        # limita el largo de los campos de texto
        if df_stata[col].dtype.name == "object":
            df_stata[col] = df_stata[col].astype(str).str[:str_limit]

        # elimina los valores infinitos de los tipos decimales
        elif "float" in df_stata[col].dtype.name:
            df_stata[col] = df_stata[col].apply(
                lambda x: np.nan if np.isinf(x) else x)

    df_stata.to_stata(path, write_index=False)


class FileWrapper:

    def __init__(self, filepath):
        self.filepath = filepath

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
