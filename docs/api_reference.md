# Referencia API

La API de Series de Tiempo permite obtener datos de una o más series, permitiendo hacer filtros por el índice de tiempo, cambios de granularidad en la dimensión temporal y cambios en la unidad de los valores de la serie, entre otras operaciones.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Tabla de parámetros](#tabla-de-par%C3%A1metros)
- [`ids`](#ids)
- [`representation_mode`](#representation_mode)
- [`collapse`](#collapse)
- [`collapse_aggregation`](#collapse_aggregation)
- [`limit`](#limit)
- [`start`](#start)
- [`start_date`](#start_date)
- [`end_date`](#end_date)
- [`format`](#format)
- [`header`](#header)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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
        <td>ids</td>
        <td>Si</td>
        <td>Lista de caracteres alfanuméricos separados por comas.
                    <br>Contiene la especificación de las series a consultar, junto a transformaciones y operaciones.</td>
        <td>N/A</td>
        <td>ids=2.4_DGI_1993_T_19,134.2_B_0_0_6</td>
    </tr>
    <tr>
        <td>representation_mode</a></td>
        <td>No</td>
        <td>Uno de: value, change, percent_change</td>
        <td>value</td>
        <td>representation_mode=percent_change</td>
    </tr>
    <tr>
        <td>collapse</a></td>
        <td>No</td>
        <td>Uno de: day, month, quarter, year</td>
        <td>La granularidad propia de la serie.</td>
        <td>collapse=year
                    <br>collapse=quarter</td>
    </tr>
    <tr>
        <td>collapse_aggregation</a></td>
        <td>No</td>
        <td>Uno de: avg, sum, min, max</td>
        <td>avg</td>
        <td>collapse_aggregation=sum</td>
    </tr>
    <tr>
        <td>limit</a></td>
        <td>No</td>
        <td>Número entero positivo, no mayor que 100.</td>
                <td class="s4" dir="ltr">100</td>
        <td>limit=50</td>
    </tr>
    <tr>
        <td>start</a></td>
        <td>No</td>
        <td>Número entero positivo o 0.</td>
                <td class="s4" dir="ltr">0</td>
        <td>start=100</td>
    </tr>
    <tr>
        <td>start_date</a></td>
        <td>No</td>
        <td>Fecha y hora en formato ISO 8601.
                    <br>
                    <br>Si no se especifica este parámetro, se devuelven todos los datos disponibles para la serie o series desde el primer valor.</td>
        <td>N/A</td>
        <td>start_date=2016-11-30</td>
    </tr>
    <tr>
        <td>end_date</td>
        <td>No</td>
        <td>Fecha y hora en formato ISO 8601.
                    <br>
                    <br>Si no se especifica este parámetro, se devuelven todos los datos disponibles para la serie o series hasta el último dato disponible.</td>
        <td>N/A</td>
        <td>end_date=2016-11-30</td>
    </tr>
    <tr>
        <td>format</a></td>
        <td>No</td>
        <td>Uno de: json, csv</td>
        <td>json</td>
        <td>format=csv</td>
    </tr>
    <tr>
        <td>header</td>
        <td>No</td>
        <td>Uno de: names, ids</td>
        <td>names</td>
        <td>header=ids</td>
    </tr>
    <tr>
        <td>sort</td>
        <td>No</td>
        <td>Uno de: asc, desc</td>
        <td>asc</td>
        <td>sort=desc</td>
    </tr>
</table>

## `ids`

Lista separada por comas de los identificadores de las series a seleccionar para armar la respuesta. Los datos del resultado de la llamada tendrán una columna por cada serie seleccionada.

Este parámetro es requerido para la llamada. En caso de no suministrarse, se devolverá un error.

Cada identificador de serie podrá ser sufijado con:

* Un indicador de modo de representación (`representation_mode`).
* Un tipo de agregación para modificar la frecuencia de muestreo (`collapse_aggregation`).

Cuando estos atributos se utilizan como parte del parámetro ids, se deben separar usando el caracter ":". El orden de los componentes no incide en el resultado de la operación.

Ejemplos:

    ids=2.4_DGI_1993_T_19,134.2_B_0_0_6:change


***Especificando el modo de representación***

Para especificar el modo de representación para una serie en particular en el parámetro `ids` es necesario sufijar el identificador de la serie con _:<nombre del representation_mode>_.

Los modos de representación disponibles son los mismos que para el parámetro `representation_mode`.

## `representation_mode`

Este parámetro indica el modo de representación de las series, y se aplica a todas aquéllas que no tengan el modo de representación indicado en el parámetro ids.

El modo de representación por defecto es el valor medido en la serie (`value`).

Los modos de representación disponibles son:

* *value*: Es el modo de representación por defecto. Devuelve el valor medido en la serie.
* *change*: Devuelve la diferencia absoluta entre el valor del período t y el de t-1.
* *percent_change*: Devuelve la variación porcentual entre el valor del período t y el de t-1.

## `collapse`

El parámetro collapse modifica la frecuencia de muestreo de los datos de la serie, permitiendo indicar un método para combinar los valores, cuando corresponda.

Los siguientes valores están disponibles para ser usados:

* *year*: Muestra datos agregados anualmente.
* *quarter*: Muestra datos agregados trimestralmente.
* *month*: Muestra datos agregados mensualmente.
* *day*: Muestra datos agregados diariamente.

Si no se indica, se retornan los datos con la granularidad propia de la serie de datos.

Si la granularidad solicitada en el valor de collapse es menor a la granularidad propia de la serie, la consulta devolverá un error.

El parámetro `collapse` afecta de la misma manera a todas las series seleccionadas por el parámetro `ids`.

## `collapse_aggregation`

El parámetro `collapse_aggregation` se utiliza sólo cuando el parámetro collapse es especificado. Indica qué operación realizar con las mediciones agrupadas de menor granularidad que la granularidad indicada por el parámetro `collapse`.

Los valores disponibles para el parámetro son:

* *avg*: Realiza el promedio de todos los valores agrupados. Es la opción por defecto si no se indica valor para `collapse_aggregation`.
* *sum*: Suma todos los valores agrupados.
* *min*: Mínimo entre los valores agrupados.
* *max*: Máximo entre los valores agrupados.

## `limit`

Este parámetro es utilizado junto a `start` para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo, no mayor que 1000, ya que esa es la cantidad máxima de resultados devueltos por la API. El valor por defecto si no se especifica valor alguno es 100.

## `start`

Este parámetro es utilizado junto a `limit` para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo o 0. El valor por defecto si no se especifica valor alguno es 0.

El `start` indica el "número de períodos después de `start_date`" (o el "número de períodos antes de `end_date`", dependiendo del ordenamiento *ASC* o *DESC* del parámetro `sort`) que se saltean desde el comienzo o el final de la serie antes de empezar a devolver valores.

## `start_date`

El parámetro `start_date` indica la fecha menor a partir de la cual se comenzarán a recolectar datos para la respuesta. Los valores cuyo índice de tiempo coincida con el valor de `start_date` se incluirán en el resultado retornado. Se utilizará como filtro sobre el índice de tiempo de las series de datos.

## `end_date`

El parámetro `end_date indica la fecha mayor hasta la cual se recolectarán datos para la respuesta. Los valores cuyo índice de tiempo coincida con el valor de `end_date se incluirán en el resultado retornado. Se utilizará como filtro sobre el índice de tiempo de las series de datos.

## `format`

Especifica el formato de la respuesta, siendo json el valor por defecto.

Las opciones disponibles para este parámetro son:

* *json*: Devuelve un objeto json con datos y metadatos de las series.
* *csv*: Devuelve las series seleccionadas en formato separado por comas. Este tipo de formato no incluye metadatos de las series seleccionadas.

## `header`

Especifica los atributos de las series a utilizar como *headers* (cabeceras) de las columnas del archivo CSV generado. Por defecto usa *names*, que son los títulos de las series.

Las opciones disponibles son:

* *names*: títulos de las series, por ejemplo **oferta_global_pib**.
* *ids*: identificadores únicos de las series, los mismos pasados al parámetro `ids`.

