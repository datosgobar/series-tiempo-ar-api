# Generar identificadores

Los identificadores de las series son códigos únicos en la Administración Pública Nacional que identifican a una serie individual. Se usan en la API para solicitar los datos de una serie.

!!! note "Identificadores de series"
    [https://apis.datos.gob.ar/series/api/series/?ids=**tmi_arg**](https://apis.datos.gob.ar/series/api/series/?ids=tmi_arg)
    [https://apis.datos.gob.ar/series/api/series/?ids=**AGRO_0001**](https://apis.datos.gob.ar/series/api/series/?ids=AGRO_0001)
    [https://apis.datos.gob.ar/series/api/series/?ids=**tcrse_IBMDNk**](https://apis.datos.gob.ar/series/api/series/?ids=tcrse_IBMDNk)
    [https://apis.datos.gob.ar/series/api/series/?ids=**defensa_FAA_0006**](https://apis.datos.gob.ar/series/api/series/?ids=defensa_FAA_0006)
    [https://apis.datos.gob.ar/series/api/series/?ids=**148.3_INIVELNAL_DICI_M_26**](https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26)

Cuando un organismo comienza a publicar series de tiempo, es muy importante diseñar o elegir una convención o sistema de nomenclatura para generar los identificadores de las series del organismo, que cumpla con las siguientes propiedades:

## Propiedades de un buen identificador

* **No cambia en el tiempo, nunca**.
* **Es único dentro de toda la base**.
* **No se pisa o se confunde con otro**.
* **Es relativamente corto**.

## Sistemas de nomenclatura propuestos

### Autoincremental numérico

Numera las series en orden a medida que se van publicando por primera vez, empieza en el número 1 y se incrementa sucesivamente con cada serie nueva.

Debe agregarse un prefijo con el identificador del catálogo (o similar) para evitar la duplicidad de códigos con otro organismo. Conviene comenzar en 0001 en lugar de 1 para que el largo del identificador sea el mismo (o al menos hasta que se superen las 10 mil series publicadas).

* AGRO_0001
* AGRO_0002
* AGRO_0003

También se puede combinar con algún código, generando una clasificación intermedia.

* defensa_ARA_0001
* defensa_FAA_0001
* defensa_EA_0001
* defensa_ARA_0002
* defensa_FAA_0002
* defensa_EA_0002

### Aleatorio

Elige una cadena de texto aleatoria de X cantidad de dígitos para cada serie nueva.

Se puede usar un [generador aleatorio de textos](https://passwordsgenerator.net/) usando 8 dígitos, números, letras minúsculas y letras mayúsculas. Se recomienda excluir caracteres especiales para facilitar la legibilidad del identificador y, si bien 8 dígitos suelen garantizar que no habrá duplicidad, debe chequearse que el id no exista ya en la base.

* QlB4ZASI
* 2tbCLAVM
* lYhCfv8r

También se puede combinar con el identificador de catálogo o un código diferente como prefijo, y usar menos caracteres aleatorios (6 o 4).

* tcrse_IBMDNk
* tcrse_k22ckW
* tcrse_GBz3WO

### Codificado

Codifica características de las series según un criterio predefinido y/o utiliza siglas o acrónimos para abreviar su nombre.

Este sistema suele buscar aumentar la legibilidad del identificador, para el usuario avanzado que puede entender el sistema de nomenclatura utilizado y ahorrar tiempo en la búsqueda de series del mismo dataset o temática.

* tmi_arg (Tasa de Mortalidad Infantil de Argentina)
* tmi_02 (Tasa de Mortalidad Infantil de Ciudad Autónoma de Buenos Aires)
* tmi_06 (Tasa de Mortalidad Infantil de la Provincia de Buenos Aires)

Debe tenerse **especial cuidado en no generar identificadores fácilmente duplicables** en el contexto de la Administración Pública Nacional o que puedan prestar a confusión con otras series diferentes.

En caso de optar por este sistema, algunas características o dimensiones de apertura de los valores de las series deben codificarse según los siguientes criterios:

#### Unidades territoriales

* Usar `arg` para señalar series de alcance nacional o el [código ISO alpha-3](http://www.indec.gov.ar/ftp/cuadros/territorio/codigo_paises.xls) para series de alcance nacional de otros países (`bra`, `usa`, etc)
* Usar el código numérico de INDEC para señalar series de alcance [provincial](https://apis.datos.gob.ar/georef/api/provincias?campos=basico) o [departamental](https://apis.datos.gob.ar/georef/api/departamentos?campos=basico).

#### Siglas o acrónimos

* Usar siglas o acrónimos que definen la variable **al comienzo del identificador** de la serie. Por ejemplo: TCRSE significa Tipo de Cambio Real Sectorial Efectivo, y se utiliza como prefijo de las distintas series derivadas disponibles.

    - tcrse_IBMDNk
    - tcrse_k22ckW
    - tcrse_GBz3WO

## Ejemplos a evitar

Los identificadores son códigos, no son nombres o descripciones. Buscan ser breves y, por sobre todo, ser permanentes en el tiempo.

Los nombres o descripciones orientados al usuario final suelen generar URLs de llamada a la API demasiado largas (y poco prácticas) y corren el riesgo de perder vigencia en el tiempo, a medida que el área cambia o mejora las descripciones de sus series o modifica sus criterios o convenciones.

* "indice_precios_nivel_general" (se puede duplicar fácilmente con otras series, es relativamente largo y puede cambiar, es un texto más adecuado para ser el título o encabezado de columna de una serie).
* "Indice de Precios Nivel General" (contiene espacios -lo que complica el uso de URLs-, se puede duplicar fácilmente, puede cambiar y es demasiado largo, es un texto más adecuado para ser la descripción de una serie).


