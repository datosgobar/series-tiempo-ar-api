<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
 

- [Referencia API: search](#referencia-api-search)
  - [Tabla de parámetros](#tabla-de-parametros)
    - [`q`](#q)
    - [`dataset_theme`, `units`, `dataset_publisher_name`, `dataset_source`, `catalog_id`](#dataset_theme-units-dataset_publisher_name-dataset_source-catalog_id)
    - [`limit`](#limit)
    - [`start`](#start)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Referencia API: search

Recurso: `/search`

El recurso `/search` permite buscar series a partir de un texto, proporcionando además algunos filtros (ej.: por tema o por unidades de las series).

## Tabla de parámetros

<table>
    <tr>
        <th>Nombre</th>
        <th>Requerido</th>
        <th>Descripción</th>
        <th>Default</th>
        <th>Ejemplos</th>
    </tr>
    <tr>
        <td>q</td>
        <td>No</td>
        <td>Texto</td>
        <td>N/A</td>
        <td>q=ipc</td>
    </tr>
    <tr>
        <td>dataset_theme</td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/dataset_theme">/search/dataset_theme</a></td>
        <td>N/A</td>
        <td>dataset_theme="Finanzas Públicas"</td>
    </tr>
    <tr>
        <td>units</td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/field_units">/search/field_units</a></td>
        <td>N/A</td>
        <td>units="Millones de pesos"</td>
    </tr>
    <tr>
        <td>dataset_publisher_name</td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/dataset_publisher_name">/search/dataset_publisher_name</a></td>
        <td>N/A</td>
        <td>dataset_publisher_name="Subsecretaría de Programación Macroeconómica."</td>
    </tr>
    <tr>
        <td>dataset_source</td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/dataset_source">/search/dataset_source</a></td>
        <td>N/A</td>
        <td>dataset_source="Ministerio de Hacienda"</td>
    </tr>
    <tr>
        <td>catalog_id</td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/catalog_id">/search/catalog_id</a></td>
        <td>N/A</td>
        <td>catalog_id="sspm"</td>
    </tr>
    <tr>
        <td>limit</td>
        <td>No</td>
        <td>Número entero positivo, no mayor que 1000.</td>
        <td class="s4" dir="ltr">10</td>
        <td>limit=50</td>
    </tr>
    <tr>
        <td>start/td>
        <td>No</td>
        <td>Número entero positivo o 0.</td>
        <td class="s4" dir="ltr">0</td>
        <td>start=100</td>
    </tr>
    <tr>
        <td>aggregations</td>
        <td>No</td>
        <td>N/A</td>
        <td class="s4" dir="ltr">N/A</td>
        <td>N/A</td>
    </tr>
    <tr>
        <td>sort_by</td>
        <td>No</td>
        <td>Texto, uno de los listados en la sección del parámetro</td>
        <td class="s4" dir="ltr">'relevance'</td>
        <td>sort_by=hits_90_days</td>
    </tr>
    <tr>
        <td>sort</td>
        <td>No</td>
        <td>Texto, puede ser 'asc' o 'desc'</td>
        <td class="s4" dir="ltr">'desc'</td>
        <td>sort=asc</td>
    </tr>    
</table>

### `q`

Texto de entrada a buscar en la base de series de tiempo. Puede ser abritrariamente largo, pero se recomienda ingresar una o más palabras clave.

### `dataset_theme`, `units`, `dataset_publisher_name`, `dataset_source`, `catalog_id`

**Estos parámetros pueden ser usados como filtros en los resultados de la búsqueda**. Al aplicarse, se muestran únicamente aquellos resultados que sean compatibles con la especificación.

Por ejemplo: un pedido con `units=Millones de pesos` sólo contendrá series de tiempo que estén expresadas en millones de pesos.

**Los términos que aceptan estos parámetros son especificados en _recursos auxiliares_** que devuelven la lista entera de valores aceptados en los filtros.

Por ejemplo: un pedido a [`/search/field_units`](https://apis.datos.gob.ar/series/api/search/field_units/) devuelve una lista de los términos que se le pueden pasar al parámetro `units`. Cualquier otra opción devolverá una lista vacía de resultados (al no haber coincidencias). Consultar la tabla de parámetros para ver los endpoints auxiliares.

Se pueden armar consultas que filtren por más de un valor, separando los valores deseados por `||`. Por ejemplo: `units=Pesos||Millones de pesos`.

### `limit`

Este parámetro es utilizado junto a [`start`](#start) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo, no mayor que 1000, ya que esa es la cantidad máxima de resultados devueltos por la API. El valor por defecto si no se especifica valor alguno es 10.

### `start`

Este parámetro es utilizado junto a [`limit`](#limit) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo o 0. El valor por defecto si no se especifica valor alguno es 0.

El [`start`](#start) indica el "número de resultados después del inicio" que se saltea el buscador para el armado de la respuesta.

### `aggregations`

La presencia de este parámetro agrega un objeto nuevo a la respuesta de la API bajo la clave `aggregations`, que contiene la cantidad de ocurrencias totales de la búsqueda discriminando por los distintos filtros posibles. Si el parámetro no está presente, no se calculan las agregaciones.

 Un ejemplo posible de la respuesta:

```json
{
  "aggregations": {
    "dataset_theme": [
      {
        "label": "Finanzas Públicas",
        "series_count": 904
      },
      {
        "label": "Precios",
        "series_count": 522
      },
      {
        "label": "Sector Externo",
        "series_count": 21
      }
    ],
    "units": [
      {
        "label": "Millones de pesos",
        "series_count": 904
      },
      {
        "label": "Índice",
        "series_count": 509
      },
      {
        "label": "Millones de dólares",
        "series_count": 21
      },
      {
        "label": "Variación Porcentual",
        "series_count": 12
      },
      {
        "label": "Variación intermensual",
        "series_count": 1
      }
    ],
    "dataset_publisher_name": [
      {
        "label": "Subsecretaría de Programación Macroeconómica.",
        "series_count": 1447
      }
    ],
    "dataset_source": [
      {
        "label": "Ministerio de Hacienda",
        "series_count": 925
      },
      {
        "label": "Instituto Nacional de Estadística y Censos (INDEC)",
        "series_count": 522
      }
    ],
    "catalog_id": [
      {
        "label": "sspm",
        "series_count": 1447
      }
    ]
  }
}
```

### `sort_by`

Este parámetro permite ordenar los resultados obtenidos según el valor que cada uno posee para cierto campo, de manera descendente (es decir, de mayor a menor según dicho valor)

Los valores que puede adoptar el mismo son:

- `relevance`: Valor por defecto, para que los resultados se ordenen por relevancia en base a los demás filtros y parámetros
- `hits_90:days`: Ordena los resultados según cuántos accesos tuvieron las series en los últimos 90 días (el campo `hits` de la response)
- `frequency`: Ordena los resultados según la periodicidad de la serie (de menor a mayor granularidad: anual, semestral, trimestral, mensual, semanal y diaria). Un orden descendente implica de mayor a menor granularidad

### `sort`

Este parámetro permite determinar el sentido del ordenamiento de los resultados, es decir, ascendente (`asc`, de menor a mayor) o descendente (`desc`, de mayor a menor). 

Debe tenerse en cuenta que, si se ordena por relevancia, el orden tan sólo puede ser descendente; si se eligiese otro criterio de ordenamiento en el parámetro `sort`, cualquier sentido es válido
