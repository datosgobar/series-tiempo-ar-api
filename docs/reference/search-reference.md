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
        <td>dataset_theme</a></td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/dataset_theme">/search/dataset_theme</a></em></td>
        <td>N/A</td>
        <td>dataset_theme="Finanzas Públicas"</td>
    </tr>
    <tr>
        <td>units</a></td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/field_units">/search/field_units</a></td>
        <td>N/A</td>
        <td>units="Millones de pesos"</td>
    </tr>
    <tr>
        <td>dataset_publisher_name</a></td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/dataset_publisher_name">/search/dataset_publisher_name</a></td>
        <td>N/A</td>
        <td>dataset_publisher_name="Subsecretaría de Programación Macroeconómica."</td>
    </tr>
    <tr>
        <td>dataset_source</a></td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/dataset_source">/search/dataset_source</a></td>
        <td>N/A</td>
        <td>dataset_source="Ministerio de Hacienda"</td>
    </tr>
    <tr>
        <td>catalog_id</a></td>
        <td>No</td>
        <td>Uno de los valores listados en <a href="https://apis.datos.gob.ar/series/api/search/catalog_id">/search/catalog_id</a></td>
        <td>N/A</td>
        <td>catalog_id="sspm"</td>
    </tr>
    <tr>
        <td>limit</a></td>
        <td>No</td>
        <td>Número entero positivo, no mayor que 1000.</td>
        <td class="s4" dir="ltr">10</td>
        <td>limit=50</td>
    </tr>
    <tr>
        <td>start</a></td>
        <td>No</td>
        <td>Número entero positivo o 0.</td>
        <td class="s4" dir="ltr">0</td>
        <td>start=100</td>
    </tr>
</table>

### `q`

Texto de entrada a buscar en la base de series de tiempo. Puede ser abritrariamente largo, pero se recomienda ingresar una o más palabras clave.

### `dataset_theme`, `units`, `dataset_publisher_name`, `dataset_source`, `catalog_id`

**Estos parámetros pueden ser usados como filtros en los resultados de la búsqueda**. Al aplicarse, se muestran únicamente aquellos resultados que sean compatibles con la especificación.

Por ejemplo: un pedido con `units=Millones de pesos` sólo contendrá series de tiempo que estén expresadas en millones de pesos.

**Los términos que aceptan estos parámetros son especificados en _recursos auxiliares_** que devuelven la lista entera de valores aceptados en los filtros.

Por ejemplo: un pedido a [`/search/field_units`](https://apis.datos.gob.ar/series/api/search/field_units/) devuelve una lista de los términos que se le pueden pasar al parámetro `units`. Cualquier otra opción devolverá una lista vacía de resultados (al no haber coincidencias). Consultar la tabla de parámetros para ver los endpoints auxiliares.

### `limit`

Este parámetro es utilizado junto a [`start`](#start) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo, no mayor que 1000, ya que esa es la cantidad máxima de resultados devueltos por la API. El valor por defecto si no se especifica valor alguno es 10.

### `start`

Este parámetro es utilizado junto a [`limit`](#limit) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo o 0. El valor por defecto si no se especifica valor alguno es 0.

El [`start`](#start) indica el "número de resultados después del inicio" que se saltea el buscador para el armado de la respuesta.




