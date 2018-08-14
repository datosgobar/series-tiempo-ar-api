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

METADATA_URL = 'http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.2/download/series-tiempo-metadatos.csv'


def _get_endpoint(api_series_ip=None):
    BASE_URL = api_series_ip if api_series_ip else os.environ["API_SERIES_IP"]
    ENDPOINT_URL = BASE_URL + 'series/api/series/'
    return ENDPOINT_URL


def api_series_head(serie_id, api_series_ip=None):
    endpoint = _get_endpoint(api_series_ip)
    result = requests.head(
        endpoint, params={'ids': serie_id}).status_code == 200
    return result, endpoint


def main(queries_cant=None, api_series_ip=None):
    series_metadata = pd.read_csv(METADATA_URL)

    queries_cant = int(queries_cant) if queries_cant else len(
        series_metadata.serie_id.unique())
    print("Realizando {} queries de prueba".format(queries_cant))

    series_ids = series_metadata.serie_id[:queries_cant]
    result = {}
    for idx, serie_id in enumerate(series_ids):
        status_code = api_series_head(serie_id, api_series_ip)
        print("Ping serie {} de {} ({}): {}".format(
            idx + 1, len(series_ids), serie_id, status_code))

        # cuenta los resultados
        if result_code in result:
            result[status_code] += 1
        else:
            result[status_code] = 0

    print(result)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
