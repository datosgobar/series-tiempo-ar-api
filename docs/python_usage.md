# Usar en python

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
 

- [Con `requests`](#con-requests)
- [Con `pandas`](#con-pandas)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Con `requests`

Armar una función _wrapper_ que facilite construir llamadas a la API.

```python
import requests
import urllib.parse

def get_api_call(ids, **kwargs):
    API_BASE_URL = "https://apis.datos.gob.ar/series/api/"
    kwargs["ids"] = ",".join(ids)
    return "{}{}?{}".format(API_BASE_URL, "series", urllib.parse.urlencode(kwargs))
```

Una llamada válida a la API debe tener por lo menos un id de una serie válida, y luego puede tener parámetros opcionales.

```python
api_call = get_api_call(["168.1_T_CAMBIOR_D_0_0_26"], start_date="2018-08")
print(api_call)

http://apis.datos.gob.ar/series/api/series?start_date=2018-08&ids=168.1_T_CAMBIOR_D_0_0_26
```

Obtener la respuesta en un diccionario.

```python
result = requests.get(api_call).json()
print(result)

{'data': [['2018-08-01', 27.525],
  ['2018-08-02', 27.45],
  ['2018-08-03', 27.29],
  ['2018-08-04', 27.29],
  ['2018-08-05', 27.29],
  ['2018-08-06', 27.33],
  ['2018-08-07', 27.395],
  ['2018-08-08', 27.65],
  ['2018-08-09', 28.11],
  ['2018-08-10', 29.25],
  ['2018-08-11', 29.25],
  ['2018-08-12', 29.25],
  ['2018-08-13', 29.925],
  ['2018-08-14', 29.61],
  ['2018-08-15', 30.0],
  ['2018-08-16', 29.84]],
 'meta': [{'end_date': '2018-08-16',
   'frequency': 'day',
   'start_date': '2018-08-01'},
  {'catalog': {'title': 'Datos Programación Macroeconómica'},
   'dataset': {'description': 'Datos de tipo de cambio $-USD - futuro dólar . Con respecto al dólar de Estados Unidos. Frecuencia diaria.',
    'issued': '2017-09-28',
    'source': 'BCRA, MAE, Rofex y Bloomberg',
    'title': 'Tipo de Cambio $-USD - Futuro Dólar'},
   'distribution': {'downloadURL': 'http://infra.datos.gob.ar/catalog/sspm/dataset/168/distribution/168.1/download/datos-tipo-cambio-usd-futuro-dolar-frecuencia-diaria.csv',
    'title': 'Tipo de cambio $-USD - futuro dólar. Valores diarios'},
   'field': {'description': 'Tipo de Cambio BNA (Vendedor)',
    'id': '168.1_T_CAMBIOR_D_0_0_26',
    'units': 'Pesos argentinos por dólar'}}],
 'params': {'identifiers': [{'dataset': '168',
    'distribution': '168.1',
    'id': '168.1_T_CAMBIOR_D_0_0_26'}],
  'ids': '168.1_T_CAMBIOR_D_0_0_26',
  'start_date': '2018-08'}}
```

## Con `pandas`

Las llamadas a la API en CSV se pueden leer directamente a un `pandas.DataFrame`.

```python
import pandas as pd

df = pd.read_csv(get_api_call(
    ["168.1_T_CAMBIOR_D_0_0_26", "101.1_I2NG_2016_M_22", "116.3_TCRMA_0_M_36", "143.3_NO_PR_2004_A_21", "11.3_VMATC_2004_M_12"],
    format="csv", start_date=2018
))
```

```
indice_tiempo  tipo_cambio_bna_vendedor  ipc_2016_nivel_general  \
   2018-01-01                 19.023065                127.0147
   2018-02-01                 19.835179                130.2913
   2018-03-01                 20.229355                133.5028
   2018-04-01                 20.251100                136.9380
   2018-05-01                 23.600452                139.5800
   2018-06-01                 26.674333                145.0582
   2018-07-01                 27.607645                149.1178
 tipo_cambio_real_multilateral_actual  indice_serie_original  construccion
                            96.628715             144.086686    158.920762
                            96.121512             138.470530    152.630381
                            93.062453             155.570021    158.931156
                            90.715862             152.432629    149.860484
                           104.302984             160.622476    154.011846
                           114.546258                    NaN           NaN
                           107.105698                    NaN           NaN
```



<!-- ## Con `plotly` -->
