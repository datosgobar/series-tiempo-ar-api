import urllib.parse
from io import BytesIO

import chardet
import requests
import pandas as pd
from django.conf import settings
from django_datajsonar.models import Distribution

from series_tiempo_ar_api.libs.indexing.strings import NO_DISTRIBUTION_URL


def read_distribution_csv(distribution: Distribution) -> pd.DataFrame:
    url = distribution.download_url
    if url is None:
        raise ValueError(NO_DISTRIBUTION_URL.format(distribution.identifier))

    # Fix a pandas fallando en lectura de URLs no ascii
    url = url.encode('UTF-8')
    url = urllib.parse.quote(url, safe='/:?=&')

    if getattr(settings, 'TESTS_IN_PROGRESS', False):
        with open(url, 'rb') as f:
            content = f.read()
    else:
        content = requests.get(url, verify=False).content

    encoding = chardet.detect(content)['encoding']
    return pd.read_csv(BytesIO(content),
                       encoding=encoding,
                       parse_dates=[settings.INDEX_COLUMN],
                       index_col=settings.INDEX_COLUMN)
