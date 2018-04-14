# Comienzo rápido

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
 

- [Pasos](#pasos)
  - [1. Buscar series](#1-buscar-series)
  - [2. Armar consulta](#2-armar-consulta)
  - [3. Descargar o integrar consulta](#3-descargar-o-integrar-consulta)
- [Tipos de consulta](#tipos-de-consulta)
  - [Descargar una tabla con una o varias series](#descargar-una-tabla-con-una-o-varias-series)
  - [Filtrar por fechas](#filtrar-por-fechas)
  - [Cambiar la agregación temporal](#cambiar-la-agregacion-temporal)
  - [Cambiar la función de agregación temporal](#cambiar-la-funcion-de-agregaci%C3%B3n-temporal)
  - [Aplicar transformaciones](#aplicar-transformaciones)
  - [Aplicar transformaciones y cambiar la función de agregación temporal en series individuales, a la vez](#aplicar-transformaciones-y-cambiar-la-funcion-de-agregaci%C3%B3n-temporal-en-series-individuales-a-la-vez)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Pasos

### 1. Buscar series

**En datos.gob.ar**

En http://www.datos.gob.ar podés encontrar la [base completa de series de tiempo](http://datos.gob.ar/dataset/base-series-tiempo-administracion-publica-nacional).

**Descargar lista de series**: [CSV](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.2/download/series-tiempo-metadatos.csv) - [XLSX](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.6/download/series-tiempo-metadatos.xlsx) - [DTA](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.10/download/series-tiempo-metadatos.dta).

**En aplicaciones web**

* **Generador de URLs**: https://datosgobar.github.io/series-tiempo-ar-explorador
* **Buscador y visualizador**: http://series-de-tiempo-ar-graficos.netlify.com/

### 2. Armar consulta

Los ids de las series deben pasarse al parámetro `ids` del *endpoint* principal `series`:

```md
http://apis.datos.gob.ar/series/api/series?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15
```

Hay varios parámetros opcionales para hacer distintos tipos de consulta ([Ver referencia API](api_reference.md))

### 3. Descargar o integrar consulta

* Integrar con aplicaciones: usar con `format=json` y el nivel de metadatos necesario `metadata=none, only, simple o full`.
* Integrar con planillas de cálculo: usar con `format=csv` ([ver "Integración con planillas de cálculo"](spreadsheet_integration.md)).

## Tipos de consulta

### Descargar una tabla con una o varias series

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15&format=csv
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15&format=csv
)

### Filtrar por fechas

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01
)

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general hasta Diciembre de 2016*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&end_date=2016-12-01
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&end_date=2016-12-01
)

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016, hasta Diciembre de 2016*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01&end_date=2016-12-01
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01&end_date=2016-12-01
)

### Cambiar la agregación temporal

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

```md
http://apis.datos.gob.ar/series/api/series?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
)

### Cambiar la función de agregación temporal

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general, en valores trimestrales a último valor del período*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter&collapse_aggregation=end_of_period
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter&collapse_aggregation=end_of_period
)

*Tipo de cambio (último valor del período), índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
)
### Aplicar transformaciones

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016, en valores mensuales y variación porcentual*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01-01&representation_mode=percent_change
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01-01&representation_mode=percent_change
)

*Tipo de cambio, índice de precios núcleo (variación porcentual) e índice de precios nivel general (variación porcentual) desde Enero de 2016, en valores mensuales*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01
)

### Aplicar transformaciones y cambiar la función de agregación temporal en series individuales, a la vez

*Tipo de cambio (variaciones porcentuales entre los últimos valores de cada período), índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period:percent_change,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period:percent_change,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
)
