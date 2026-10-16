---
title: "Integración con planillas de cálculo"
---

## Google Drive

### 1. Modificar la configuración regional o usar el parámetro "decimal=,"

#### Usar el parámetro `decimal`

La API genera archivos CSV usando "." como separador decimal por defecto. Si tu cuenta de Google está configurada para Argentina / latinoamérica, podés agregar a todas tus llamadas a la API el argumento `&decimal=,` para que los CSVs se generen con "," como separador decimal.

:::note
[https://apis.datos.gob.ar/series/api/series/?limit=1000&metadata=full&start=0&ids=143.3_NO_PR_2004_A_21&format=csv&decimal=,](https://apis.datos.gob.ar/series/api/series/?limit=1000&metadata=full&start=0&ids=143.3_NO_PR_2004_A_21&format=csv&decimal=,)
:::

Ver uso del parámetro [`decimal`](/series-tiempo-ar-api/reference/api-reference/#decimal) en la referencia.

#### Modificar la configuración regional

Para que Google Spreadsheet lea correctamente el archivo CSV por defecto, puede elegirse “Estados Unidos” o cualquier otra región compatible como configuración regional.

![excel](assets/google_drive_letra_1.png "google_drive")
![excel](assets/google_drive_letra_2.png "google_drive")
![excel](assets/google_drive_letra_3.png "google_drive")

### 2. Importar los datos a la planilla

La función IMPORTDATA() toma la URL de la consulta a la API y trae los datos a la planilla.

![excel](assets/google_drive_letra_4.png "google_drive")
![excel](assets/google_drive_letra_5.png "google_drive")

### 3. Elegir el formato de fecha

El índice de tiempo puede verse como un número la primera vez que se importan los datos. Lo más conveniente es seleccionar toda la columna y elegir el formato en el que se desea visualizar la fecha.

![excel](assets/google_drive_letra_6.png "google_drive")
![excel](assets/google_drive_letra_7.png "google_drive")
![excel](assets/google_drive_letra_8.png "google_drive")

### 4. Modificar la URL de consulta a la API

Una vez importada la tabla por primera vez, se pueden modificar los distintos parámetros de la consulta según lo que se necesite. La tabla se actualizará con cada cambio.

![excel](assets/google_drive_letra_9.png "google_drive")
![excel](assets/google_drive_letra_10.png "google_drive")
![excel](assets/google_drive_letra_11.png "google_drive")

## Excel

### 0. Chequear que tenés instalado lo que necesitás

* **Excel 2016**: tiene todo lo necesario para integrar una URL a un CSV.
* **Excel 2013**: necesita [descargar e instalar Microsoft Power Query](https://www.microsoft.com/es-es/download/details.aspx?id=39379).
* **Excel 2010**: necesita [descargar e instalar el Service Pack 1](https://www.microsoft.com/es-ar/download/details.aspx?id=26622) y luego [descargar e instalar Microsoft Power Query](https://www.microsoft.com/es-es/download/details.aspx?id=39379).

### 1. Generar una nueva consulta desde una URL

“Datos” > “Nueva consulta” > “Desde otras fuentes” > “Desde una web”

**Nota:** si Excel está configurado para Argentina / Latinoamérica agregar a la URL de la API `&decimal=,` para que los números decimales usen "," en lugar de "." y Excel los lea correctamente. Ver uso del parámetro [`decimal`](/series-tiempo-ar-api/reference/api-reference/#decimal) en la referencia.

:::note
[https://apis.datos.gob.ar/series/api/series/?limit=1000&metadata=full&start=0&ids=143.3_NO_PR_2004_A_21&format=csv&decimal=,](https://apis.datos.gob.ar/series/api/series/?limit=1000&metadata=full&start=0&ids=143.3_NO_PR_2004_A_21&format=csv&decimal=,)
:::

![excel](assets/excel_letra_1.png "excel")
![excel](assets/excel_letra_2.png "excel")
![excel](assets/excel_letra_3.png "excel")
![excel](assets/excel_letra_4.png "excel")

### 2. Editar codificación del archivo origen

Esto **sólo es necesario si se pide a la API usar las descripciones como nombres de las columnas** (`&header=descriptions`) en lugar del texto corto que viene por defecto, formado con carateres compatibles con cualquier codificación.

La API genera los archivos CSV con codificación “Unicode UTF-8”, que no es el valor por defecto de Excel y puede generar errores en los caracteres con tildes o la "ñ".

Clic en la rueda de “Origen” > “Origen de archivo” > Elegir “Unicode UTF-8”

![excel](assets/excel_letra_5.png "excel")
![excel](assets/excel_letra_6.png "excel")
![excel](assets/excel_letra_7.png "excel")

### 3. Editar los tipos de las columnas

Excel puede no interpretar correctamente las fechas cuando Excel está configurado para Argentina / Latinoamérica.

Si éste es el caso, se debe utilizar el “Editor avanzado” para corregir el tipo de la columna "indice_tiempo" que debe ser “type date”.

![excel](assets/excel_letra_8.png "excel")
![excel](assets/excel_letra_9.png "excel")

### 4. Guardar las modificaciones y cargar la consulta

Por último, haciendo clic en “Cerrar y cargar” la consulta queda configurada en una tabla de Excel que se puede actualizar.

![excel](assets/excel_letra_14.png "excel")
