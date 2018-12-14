Se encuentran disponibles varios archivos con los mismos datos de la base de series de tiempo disponibles a través de la API. 

Los datos están para descargar en cuatro formatos:

* CSV
* XLSX
* SQL (Una base de datos SQLITE)
* DTA

Existen varios paquetes de datos por cada formato:

* Valores y metadatos desagregados: Contiene a la base entera de datos, junto con los metadatos de las series en cada indicador
* Sólo valores: Contiene a la base entera de datos, con una cantidad de metadatos de las series reducida respecto al paquete anterior
* Metadatos: Contiene a todos los metadatos de cada serie de tiempo en la base. No contiene datos (indicadores) de las series.
* Fuentes: Indicadores sobre las fuentes de datos disponibles en la base. Puede resultar útil como punto de partida para buscar series.


## Links de descarga

Los _dumps_ de la base de datos entera están disponibles bajo la siguiente ruta:
`https://apis.datos.gob.ar/series/api/dump/:dump`

Donde `:dump` puede ser uno de los siguientes archivos:

Formato CSV:

* `series-tiempo-csv.zip`
* `series-tiempo-valores-csv.zip`
* `series-tiempo-metadatos.csv`
* `series-tiempo-fuentes.csv`
 
Formato XLSX:

* `series-tiempo.xlsx`
* `series-tiempo-valores.xlsx`
* `series-tiempo-metadatos.xlsx`
* `series-tiempo-fuentes.xlsx`

Formato SQL:

La base de datos en SQL contiene a estos paquetes como tablas, todas en un único archivo.

* `series-tiempo-sqlite.zip`

Formato DTA:

* `series-tiempo-valores-dta.zip`
* `series-tiempo-metadatos.dta`
* `series-tiempo-fuentes.dta`

Notar que para el formato DTA no se disponibiliza la distribución con valores y metadatos desagregados.

Por ejemplo, la base de series de tiempo entera, junto con varios metadatos de las series, en formato XLSX, se encuentra disponible bajo

`https://apis.datos.gob.ar/series/api/dump/series-tiempo.xlsx`

## Dumps por catálogo

A su vez, también existen versiones de los datos desagregados según el *catálogo* de origen. Se encuentran en la siguiente URL de descarga:
`https://apis.datos.gob.ar/series/api/dump/:catalog/:dump`

Los catálogos se pueden consultar bajo el siguiente _endpoint_ de la API de búsqueda:
`https://apis.datos.gob.ar/series/api/search/catalog_id/`

Por ejemplo, para consultar las fuentes del catálogo `sspm` (de la Subsecretaría de Programación Macroeconómica del Ministerio de Hacienda de la Nación), en formato XLSX, se puede acceder en la siguiente URL:

`https://apis.datos.gob.ar/series/api/dump/sspm/series-tiempo-fuentes.xlsx`
