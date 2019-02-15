import random
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from io import StringIO
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
from urllib.error import HTTPError

X_SOURCE = 'API de Series de Tiempo: Test de Integración'


def read_source_csv(serie_id: str, metadata: pd.DataFrame):
    serie_metadata = metadata.loc[serie_id, :]
    if metadata is None:
        return None

    download_url = serie_metadata.distribucion_url_descarga
    title = serie_metadata.serie_titulo
    try:
        csv = pd.read_csv(download_url, parse_dates=['indice_tiempo'], index_col='indice_tiempo')
        return csv[[title]]
    except (HTTPError, KeyError):
        return None


def get_equality_array(api_df: pd.DataFrame, original_df: pd.DataFrame):
    df = pd.merge(api_df, original_df, left_index=True, right_index=True)
    api, original = df.columns
    equality = np.isclose(df[api], df[original], rtol=0.001, equal_nan=True)
    return equality


def get_series_metadata(api_url: str):
    metadata_endpoint = urljoin(api_url, 'series/api/dump/series-tiempo-metadatos.csv')
    metadata = pd.read_csv(metadata_endpoint).set_index('serie_id')
    return metadata


class IntegrationTest:

    def __init__(self, series_metadata: pd.DataFrame, fetcher, threads=10):
        """Test de integración de la API de series. A partir de los metadatos de las series
        (obtenibles a partir de un dump de metadatos), se consultan los datos de todas las
        series una vez, y se comparan con los datos originales.
        """
        self.series_metadata = series_metadata
        self.fetcher = fetcher
        self.errors = []
        self.threads = threads

    def test(self):
        self.run_concurrent()
        return self.errors

    def run_concurrent(self):
        self.series_metadata = self.series_metadata[self.series_metadata['serie_discontinuada'] == False]
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for serie_id in self.series_metadata.index:
                fs = executor.submit(self.test_serie, serie_id)
                futures.append(fs)
            concurrent.futures.wait(futures)

    def test_serie(self, serie_id):
        original_df = read_source_csv(serie_id, self.series_metadata)
        if original_df is None:
            return

        api_df = self.read_api_csv(serie_id, last=1000)
        if api_df is None:
            return

        equality = get_equality_array(api_df, original_df)
        if not all(equality):
            error_pct = pd.Series(equality).value_counts()[False] / len(equality) * 100
            self.errors.append({'serie_id': serie_id,
                                'error_pct': error_pct,
                                'api_url': self.generate_url(serie_id),
                                'distribution_url': self.series_metadata.distribucion_url_descarga[serie_id]})

    def read_api_csv(self, serie, **kwargs):
        return self.fetcher.fetch(serie, **kwargs)

    def generate_url(self, serie_id):
        return self.fetcher.get_url(serie_id)



class HttpSeriesFetcher:
    def __init__(self, api_url: str):
        self.series_endpoint = urljoin(api_url, 'series/api/series/')
        self.metadata_endpoint = urljoin(api_url, 'series/api/dump/series-tiempo-metadatos.csv')

    def fetch(self, serie_id: str, **kwargs):
        call_params = {'ids': serie_id, 'format': 'csv', 'cache': random.random()}
        call_params.update(kwargs)
        res = requests.get(self.series_endpoint,
                           params=call_params,
                           headers={'X-Source': X_SOURCE})

        if not res.ok:
            return None

        csv = StringIO(res.content.decode('utf8'))
        api_csv = pd.read_csv(csv, parse_dates=['indice_tiempo'], index_col='indice_tiempo')

        return api_csv

    def get_url(self, serie_id: str):
        return f'{self.series_endpoint}?ids={serie_id}&last=1000&format=csv'


def run():
    args = get_argparser()
    metadata = get_series_metadata(args.api_url)
    results = IntegrationTest(series_metadata=metadata,
                              fetcher=HttpSeriesFetcher(api_url=args.api_url)).test()

    if results:
        pd.DataFrame(results).set_index('serie_id').to_csv(args.output)
        print(f"Resultados escritos a {args.output}")
        return

    print("Todas las series OK!")


def get_argparser():
    import argparse
    parser = argparse.ArgumentParser(description="Test de integración de la API de series de tiempo. Itera sobre todas "
                                                 "las series (según el dump de metadatos) y consulta los últimos "
                                                 "datos de todas las series disponibles, comparándo el resultado con "
                                                 "los datos de su fuente original.")
    parser.add_argument('api_url', type=str, help='URL de la instancia de la API a testear')
    parser.add_argument('--output',
                        type=str,
                        default='integration_test.csv',
                        help='Ruta a escribir el csv de resultados')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    run()
