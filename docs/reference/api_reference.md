# Referencia API

Endpoint: `/series`

La API de Series de Tiempo permite obtener datos de una o más series, permitiendo hacer filtros por el índice de tiempo, cambios de granularidad en la dimensión temporal y cambios en la unidad de los valores de la serie, entre otras operaciones.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
 

- [Tabla de parámetros](#tabla-de-parametros)
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
    - [`sort`](#sort)
    - [`metadata`](#metadata)
    - [`decimal`](#decimal)
    - [`flatten`](#flatten)

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
        <td>Lista de caracteres alfanuméricos separados por comas.<br><br>Contiene la especificación de las series a consultar, junto a transformaciones y operaciones.</td>
        <td>N/A</td>
        <td>ids=2.4_DGI_1993_T_19,134.2_B_0_0_6</td>
    </tr>
    <tr>
        <td>representation_mode</a></td>
        <td>No</td>
        <td>Uno de: <em>value, change, percent_change, percent_change_a_year_ago</em></td>
        <td>value</td>
        <td>representation_mode=percent_change</td>
    </tr>
    <tr>
        <td>collapse</a></td>
        <td>No</td>
        <td>Uno de: <em>day, week, month, quarter, year</em></td>
        <td>La frecuencia propia de la serie</td>
        <td>collapse=year<br>collapse=quarter</td>
    </tr>
    <tr>
        <td>collapse_aggregation</a></td>
        <td>No</td>
        <td>Uno de: <em>avg, sum, end_of_period, min, max</em></td>
        <td>avg</td>
        <td>collapse_aggregation=sum</td>
    </tr>
    <tr>
        <td>limit</a></td>
        <td>No</td>
        <td>Número entero positivo, no mayor que 1000.</td>
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
        <td>Fecha y hora en formato ISO 8601.<br><br>Si no se especifica este parámetro, se devuelven los datos disponibles para la serie o series desde el valor más antiguo.</td>
        <td>N/A</td>
        <td>start_date=2016-11-30<br>start_date=2016-11<br>start_date=2016</td>
    </tr>
    <tr>
        <td>end_date</td>
        <td>No</td>
        <td>Fecha y hora en formato ISO 8601.<br><br>Si no se especifica este parámetro, se devuelven los datos disponibles para la serie o series hasta el valor más reciente.</td>
        <td>N/A</td>
        <td>end_date=2016-11-30<br>end_date=2016-11<br>end_date=2016</td>
    </tr>
    <tr>
        <td>format</a></td>
        <td>No</td>
        <td>Uno de: <em>json, csv</em></td>
        <td>json</td>
        <td>format=csv</td>
    </tr>
    <tr>
        <td>header</td>
        <td>No</td>
        <td>Uno de: <em>titles, ids, descriptions</em></td>
        <td>titles</td>
        <td>header=ids</td>
    </tr>
    <tr>
        <td>sort</td>
        <td>No</td>
        <td>Uno de: <em>asc, desc</em></td>
        <td>asc</td>
        <td>sort=desc</td>
    </tr>
    <tr>
        <td>metadata</td>
        <td>No</td>
        <td>Uno de: <em>none, simple, full, only</em></td>
        <td>simple</td>
        <td>metadata=none</td>
    </tr>
    <tr>
        <td>decimal</td>
        <td>No</td>
        <td>Caracter utilizado para los decimales.<br><br>Uno de: <em>"," o "."</em></td>
        <td>.</td>
        <td>metadata=,</td>
    </tr>
    <tr>
        <td>flatten</td>
        <td>No</td>
        <td>Aplana la respuesta de metadatos en un objeto con un único nivel (sin objetos anidados). No es necesario darle valor</td>
        <td></td>
        <td>flatten</td>
    </tr>
</table>

### `ids`

Lista separada por comas de los identificadores de las series a seleccionar para armar la respuesta. Los datos del resultado de la llamada tendrán una columna por cada serie seleccionada, en el mismo orden.

Este parámetro es requerido para la llamada. En caso de no suministrarse, se devolverá un error.

Cada identificador de serie podrá ser sufijado con:

* Un modo de representación ([`representation_mode`](#representation_mode)).
* Una función de agregación temporal ([`collapse_aggregation`](#collapse_aggregation)).

Cuando estos atributos se utilizan como parte del parámetro `ids`, se deben separar usando el caracter ":". El orden de los componentes no incide en el resultado de la operación.

Ejemplos:

```md
ids=2.4_DGI_1993_T_19,134.2_B_0_0_6:change
ids=2.4_DGI_1993_T_19,134.2_B_0_0_6:sum:change
ids=2.4_DGI_1993_T_19,134.2_B_0_0_6:change:sum
ids=2.4_DGI_1993_T_19:percent_change,134.2_B_0_0_6:sum:change
ids=2.4_DGI_1993_T_19:end_of_period:percent_change,134.2_B_0_0_6:sum:change
```

### `representation_mode`

Este parámetro indica el modo de representación de las series, y se aplica a todas aquéllas que no tengan otro modo de representación distinto indicado en el parámetro [`ids`](#ids) en forma individual.

El modo de representación por defecto es el valor medido en la serie (*value*).

Los modos de representación disponibles son:

* *value*: Es el modo de representación por defecto. Devuelve el valor medido en la serie.
* *change*: Devuelve la diferencia absoluta entre el valor del período t y el de t-1.
* *percent_change*: Devuelve la variación porcentual entre el valor del período t y el de t-1.
* *percent_change_a_year_ago*: Devuelve la variación porcentual entre el valor del período t y el del período t equivalente de hace un año atrás.

Las funciones de transformación disponibles en [`representation_mode`](#representation_mode) también pueden especificarse para **series individuales** usando la notación `:percent_change` junto al id de la serie:

[`http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6,135.1_M_0_0_6:percent_change&collapse=year&start_date=2010`](http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6,135.1_M_0_0_6:percent_change&collapse=year&start_date=2010
)

[`http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6:percent_change_a_year_ago,135.1_M_0_0_6:percent_change&collapse=year&start_date=2010`](http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6:percent_change_a_year_ago,135.1_M_0_0_6:percent_change&collapse=year&start_date=2010
)

El parámetro [`representation_mode`](#representation_mode) seguirá afectando a todas las series para las cuales no se especifique individualmente una función de transformación.

### `collapse`

El parámetro [`collapse`](#collapse) modifica la frecuencia de muestreo de los datos de la serie o las series solicitadas. Debe usarse en combinación con [`collapse_aggregation`](#collapse_aggregation) para indicar una funnción de agregación temporal, cuando corresponda.

Las opciones disponibles son:

* *year*: Muestra datos agregados anualmente.
* *quarter*: Muestra datos agregados trimestralmente.
* *month*: Muestra datos agregados mensualmente.
* *week*: Muestra datos agregados semanalmente.
* *day*: Muestra datos agregados diariamente.

Si no se indica, se retornan los datos con la **frecuencia original de la serie**.

Si se solicitan **múltiples series de distintas frecuencias**, se utilizará la menor frecuencia de todas ellas (Ej.: si se solicitan a la vez una serie diaria, una mensual y una trimestral, se convertirán todas las series a la frecuencia trimestral).

Si la granularidad temporal solicitada en el valor de [`collapse`](#collapse) es menor a la granularidad propia de alguna de las series solicitadas, la consulta devolverá un error.

El parámetro [`collapse`](#collapse) afecta globalmente a todas las series seleccionadas por el parámetro [`ids`](#ids) en la llamada.

### `collapse_aggregation`

El parámetro [`collapse_aggregation`](#collapse_aggregation) indica la función de agregación temporal que debe usarse para homogeneizar la frecuencia temporal de todas las series solicitadas (Ej.: qué operación realizar para convertir una serie mensual en anual).

Esta función de agregación actuará sobre:

* Las series agrupadas de mayor granularidad temporal (frecuencia más alta) que la granularidad indicada por el parámetro [`collapse`](#collapse)
* En caso de que no se especifique el parámetro [`collapse`](#collapse), las series agrupadas de mayor granularidad temporal que la de la serie de menor frecuencia temporal.

Los valores disponibles para el parámetro son:

* *avg*: Realiza el promedio de todos los valores agrupados. Es la opción por defecto si no se indica valor para [`collapse_aggregation`](#collapse_aggregation).
* *sum*: Suma todos los valores agrupados.
* *end_of_period*: Último valor del período.
* *min*: Mínimo entre los valores agrupados.
* *max*: Máximo entre los valores agrupados.

Las funciones de agregación temporal disponibles en [`collapse_aggregation`](#collapse_aggregation) también pueden especificarse para **series individuales** usando la notación `:sum` junto al id de la serie:

[`http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6,135.1_M_0_0_6:sum&collapse=year&start_date=2010`](http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6,135.1_M_0_0_6:sum&collapse=year&start_date=2010
)

[`http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6:end_of_period,135.1_M_0_0_6:sum&collapse=year&start_date=2010`](http://apis.datos.gob.ar/series/api/series?ids=135.1_M_0_0_6:end_of_period,135.1_M_0_0_6:sum&collapse=year&start_date=2010
)

El parámetro [`collapse_aggregation`](#collapse_aggregation) seguirá afectando a todas las series para las cuales no se especifique individualmente una función de agregación temporal.

### `limit`

Este parámetro es utilizado junto a [`start`](#start) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo, no mayor que 1000, ya que esa es la cantidad máxima de resultados devueltos por la API. El valor por defecto si no se especifica valor alguno es 100.

### `start`

Este parámetro es utilizado junto a [`limit`](#limit) para controlar el paginado de los resultados devueltos por la API. Debe especificarse un número entero positivo o 0. El valor por defecto si no se especifica valor alguno es 0.

El [`start`](#start) indica el "número de períodos después de [`start_date`](#start_date)" (o el "número de períodos antes de [`end_date`](#end_date)", dependiendo del ordenamiento *asc* o *desc* del parámetro [`sort`](#sort)) que se saltean desde el comienzo o el final de la serie antes de empezar a devolver valores.

### `start_date`

El parámetro [`start_date`](#start_date) indica la fecha menor a partir de la cual se comenzarán a recolectar datos para la respuesta. Los valores cuyo índice de tiempo coincida con el valor de [`start_date`](#start_date) se incluirán en el resultado retornado. Se utilizará como filtro sobre el índice de tiempo de las series de datos.

### `end_date`

El parámetro [`end_date`](#end_date) indica la fecha mayor hasta la cual se recolectarán datos para la respuesta. Los valores cuyo índice de tiempo coincida con el valor de [`end_date`](#end_date) se incluirán en el resultado retornado. Se utilizará como filtro sobre el índice de tiempo de las series de datos.

### `format`

Especifica el formato de la respuesta, siendo *json* el valor por defecto.

Las opciones disponibles son:

* *json*: Devuelve un objeto json con datos y metadatos de las series.
* *csv*: Devuelve las series seleccionadas en formato separado por comas. Este tipo de formato no incluye metadatos de las series seleccionadas.

### `header`

Especifica los atributos de las series a utilizar como *headers* (cabeceras) de las columnas del archivo CSV generado. Por defecto usa *titles*, que son los títulos de las series.

Las opciones disponibles son:

* *titles*: Títulos de las series, por ejemplo **oferta_global_pib** (default).
* *ids*: Identificadores únicos de las series, los mismos pasados al parámetro `ids`.
* *descriptions*: Descripciones completas de las series, por ejemplo **Plazo fijo entre 60-89 días en millones de pesos. Categoría II-VI**

### `sort`

Especifica el orden temporal de los resultados devueltos, siendo *asc* el valor por defecto.

Las opciones disponibles son:

* *asc*: Se devuelven los valores más antiguos primero (default).
* *desc*: Se devuelven los valores más recientes primero.

### `metadata`

Especifica el nivel de detalle de metadatos requerido por el usuario, siendo *simple* el valor por defecto. Sólo aplica cuando `format=json`.

Las opciones disponibles son:

* *none*: No se devuelven metadatos, sólo datos.
* *only*: No se devuelven datos, sólo metadatos.
* *simple*: Se devuelven los metadatos más importantes para comprender y utilizar las series (default).
* *full*: Se devuelven todos los metadatos disponibles que tengan relación con cada serie.

### `decimal`

Especifica el caracter utilizado para los números decimales, siendo *.* el valor por defecto. Sólo aplica cuando `format=csv`.

Las opciones disponibles son:

* *,*: Coma.
* *.*: Punto.

### `flatten`

Especifica si la respuesta de los metadatos de las series pedidas deberían devolverse en una jerarquía _plana_.

Cuando el parámetro no es incluido, la respuesta tiene la siguiente estructura:
```
    {
        "catalog": [<catalog_meta>],
        "dataset": [<dataset_meta>],
        "distribution": [<distribution_meta>],
        "field": [<field_meta>],
    }
```

Una query con parámetro flatten incluido tendrá la siguiente respuesta de metadatos:

```
    {
        catalog_meta1: ...,
        catalog_meta2: ...,
        dataset_meta1: ...,
        <nivel>_<meta_key>: <meta_value>
        ...
    }
```
