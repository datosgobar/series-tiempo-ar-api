# Condiciones de uso

## Legales

Los datos de la API de Series de Tiempo bajo las licencias aplicadas por sus publicadores, que pueden ser consultadas en la [tabla de metadatos de las series](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.2/download/series-tiempo-metadatos.csv) o en el objeto `meta` devuelto en una consulta a la API con parámetro `metadata=full`.

!!! note "[https://apis.datos.gob.ar/series/api/series/?ids=103.1_I2N_2016_M_15&metadata=full](https://apis.datos.gob.ar/series/api/series/?ids=103.1_I2N_2016_M_15&metadata=full)"

```json
    {
      "catalog": {
        "publisher": {
          "mbox": "datoseconomicos@mecon.gov.ar",
          "name": "Subsecretaría de Programación Macroeconómica."
        },
        "license": "Creative Commons Attribution 4.0",
        "description": "Catálogo de datos abiertos de la Subsecretaría de Programación Macroeconómica.",
        "language": Array[1][
          "SPA"
        ],
        "superThemeTaxonomy": "http://datos.gob.ar/superThemeTaxonomy.json",
        "issued": "2017-09-28",
        "rights": "2017-09-28",
        "modified": "2017-09-28",
        "spatial": "ARG",
        "title": "Datos Programación Macroeconómica",
        "identifier": "sspm"
      },
      "dataset": {
        "publisher": {
          "mbox": "datoseconomicos@mecon.gov.ar",
          "name": "Subsecretaría de Programación Macroeconómica."
        },
        "landingPage": "https://www.minhacienda.gob.ar/secretarias/politica-economica/programacion-macroeconomica/",
        "keyword": Array[2][
          "Información Económica al Día",
          "Precios"
        ],
        "superTheme": Array[1][
          "ECON"
        ],
        "title": "Índice de Precios al Consumidor. Por categorías. Base diciembre 2016.",
        "language": Array[1][
          "SPA"
        ],
        "issued": "2017-09-28",
        "temporal": "2016-04-01/2017-06-01",
        "source": "Instituto Nacional de Estadística y Censos (INDEC)",
        "theme": Array[1][
          {
            "label": "Precios",
            "id": "precios",
            "description": "Series de precios"
          }
        ],
        "accrualPeriodicity": "R/P1M",
        "spatial": "ARG",
        "identifier": "103",
        "license": "Creative Commons Attribution 4.0",
        "contactPoint": {
          "fn": "Subsecretaría de Programación Macroeconómica."
        },
        "accessLevel": "ABIERTO",
        "description": "Índice de Precios al Consumidor. Apertura por categorías. Base diciembre 2016."
      },
      "distribution": {
        "accessURL": "https://www.minhacienda.gob.ar/secretarias/politica-economica/programacion-macroeconomica/",
        "description": "Índice de Precios al Consumidor. Categorías. Valores mensuales. (Base diciembre 2016).",
        "format": "CSV",
        "dataset_identifier": "103",
        "issued": "2017-09-28",
        "title": "Índice de Precios al Consumidor, por categorías. Base diciembre 2016. Valores mensuales",
        "fileName": "indice-precios-al-consumidor-categorias-base-diciembre-2016-mensual.csv",
        "downloadURL": "http://infra.datos.gob.ar/catalog/sspm/dataset/103/distribution/103.1/download/indice-precios-al-consumidor-categorias-base-diciembre-2016-mensual.csv",
        "identifier": "103.1",
        "scrapingFileURL": "https://www.economia.gob.ar/download/infoeco/apendice4.xlsx",
        "frequency": "R/P1M",
        "last_hash": "355c9dd579208476c6520e8cb05c350dbfcb6b5d5b5743f30db0f8222a0cd6db38048b73ea465102c6c5d2dfa66970eb6857f4ed63cafaaf07fbde193e82979e",
        "changed": "False"
      },
      "field": {
        "distribution_identifier": "103.1",
        "description": "IPC Núcleo. Base abr 2016. Mensual",
        "title": "ipc_2016_nucleo",
        "dataset_identifier": "103",
        "specialTypeDetail": "",
        "units": "Índice Dic-2016=100",
        "type": "number",
        "id": "103.1_I2N_2016_M_15",
        "available": "true",
        "last_value": "149.8703",
        "second_to_last_value": "145.2069",
        "last_pct_change": "0.03211555373746",
        "time_index_end": "2018-08-01",
        "frequency": "R/P1M",
        "time_index_size": "29",
        "days_without_data": "14",
        "time_index_start": "2016-04-01"
      }
    }
  ]
```

## Técnicas

La API de series de tiempo se encuentra en estado *beta* de desarrollo y las cuotas de uso pueden cambiar significativamente en el futuro, dependiendo de la evolución del desarrollo y uso del servicio.

Actualmente se aplican las siguientes cuotas de uso por IP:

* Por segundo: 30 consultas
* Por minuto: 1000 consultas
* Por hora: 10000 consultas
* Por día: 50000 consultas

