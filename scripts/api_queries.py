#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Realiza queries a la API de series de tiempo para testeo."""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import os

import os
import sys
import pandas as pd
import numpy as np
import requests
from io import StringIO

BASE_URL = os.environ["API_SERIES_IP"]
METADATA_URL = 'http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.2/download/series-tiempo-metadatos.csv'
ENDPOINT_URL = BASE_URL + 'series/api/series/'


def api_series_head(serie_id):
    msg = "Pingeando serie {}".format(serie_id)
    sys.stdout.flush()
    return requests.head(
        ENDPOINT_URL, params={'ids': serie_id}).status_code == 200


def main(queries_cant=None):
    series_metadata = pd.read_csv(METADATA_URL)

    queries_cant = int(queries_cant) if queries_cant else len(
        series_metadata.serie_id.unique())
    print("Realizando {} queries de prueba".format(queries_cant))

    series_ids = series_metadata.serie_id[:queries_cant]
    for idx, serie_id in enumerate(series_ids):
        print("Ping serie {} de {} ({}): {}".format(
            idx + 1, len(series_ids), serie_id, api_series_head(serie_id)))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
