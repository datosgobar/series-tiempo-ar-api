# Referencia búsqueda

Endpoint: `/search`

Se provee un endpoint adicional para funcionar como buscador de series a partir de un texto, proporcionando además algunos filtros como por tema o por unidades de las series.

## Tabla de parámetros

<table>
    <tr>
        <td>Nombre</td>
        <td>Requerido</td>
        <td>Tipo</td>
        <td>Default</td>
        <td>Ejemplos</td>
    </tr>
    <tr>
        <td>q</td>
        <td>Si</td>
        <td>Texto</td>
        <td>N/A</td>
        <td>q=ipc</td>
    </tr>
    <tr>
        <td>dataset_theme</a></td>
        <td>No</td>
        <td>Uno de los valores listados en /search/dataset_theme</em></td>
        <td>N/A</td>
        <td>dataset_theme="Finanzas Públicas"</td>
    </tr>
    <tr>
        <td>units</a></td>
        <td>No</td>
        <td>Uno de los valores listados en /search/field_units</td>
        <td>N/A</td>
        <td>units="Millones de pesos"</td>
    </tr>
    <tr>
        <td>dataset_publisher_name</a></td>
        <td>No</td>
        <td>Uno de los valores listados en /search/dataset_publisher_name</td>
        <td>N/A</td>
        <td>dataset_publisher_name="Subsecretaría de Programación Macroeconómica."</td>
    </tr>
    <tr>
        <td>dataset_source</a></td>
        <td>No</td>
        <td>Uno de los valores listados en /search/dataset_source</td>
        <td>N/A</td>
        <td>dataset_source="Ministerio de Hacienda"</td>
    </tr>
    <tr>
        <td>catalog_id</a></td>
        <td>No</td>
        <td>Uno de los valores listados en /search/catalog_id</td>
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

Estos parámetros pueden ser usados como filtro en los resultados de la búsqueda. Al ser especificados, se aplica el filtro determinado, haciendo que se muestren únicamente aquellos resultados que sean compatibles con la especificación. Por ejemplo, si hacemos un pedido con `units=Millones de pesos`, el resultado solo contendrá series de tiempo que estén expresados en millones de dólares.

Los términos que aceptan estos parámetros son términos especificados en _endpoints auxiliares_, que devuelven la lista entera de filtros aceptados por cada endpoint. Un pedido a `/search/field_units`(http://apis.datos.gob.ar/series/api/search/field_units/), entonces, devuelve una lista de los términos que se le pueden pasar al parámetro `units`. Cualquier otra opción devolverá una lista vacía de resultados (al no haber matches). Consultar la tabla de parámetros para ver los endpoints auxiliares.

### `limit`

Este parámetro es utilizado junto a [`start`](#start) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo, no mayor que 1000, ya que esa es la cantidad máxima de resultados devueltos por la API. El valor por defecto si no se especifica valor alguno es 10.

### `start`

Este parámetro es utilizado junto a [`limit`](#limit) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo o 0. El valor por defecto si no se especifica valor alguno es 0.

El [`start`](#start) indica el "número de resultados después del inicio" que se saltea el buscador para el armado de la respuesta.




