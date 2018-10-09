# Filtrar y transformar las series

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
 

- [Descargar una tabla con una o varias series](#descargar-una-tabla-con-una-o-varias-series)
- [Filtrar por fechas](#filtrar-por-fechas)
- [Cambiar la agregación temporal](#cambiar-la-agregacion-temporal)
- [Cambiar la función de agregación temporal](#cambiar-la-funcion-de-agregaci%C3%B3n-temporal)
- [Aplicar transformaciones](#aplicar-transformaciones)
- [Aplicar transformaciones y cambiar la función de agregación temporal en series individuales, a la vez](#aplicar-transformaciones-y-cambiar-la-funcion-de-agregaci%C3%B3n-temporal-en-series-individuales-a-la-vez)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Descargar una tabla con una o varias series

El parámetro `ids` permite la consulta simultánea de hasta **40 series a la vez**, separadas por comas.

!!! note "[IPC por categorías](http://datos.gob.ar/series/api/series/?ids=103.1_I2N_2016_M_15,101.1_I2NG_2016_M_22,102.1_I2S_ABRI_M_18,102.1_I2B_ABRI_M_15,103.1_I2R_2016_M_18,103.1_I2E_2016_M_21)"

    [`http://apis.datos.gob.ar/series/api/series/?ids=103.1_I2N_2016_M_15,101.1_I2NG_2016_M_22,102.1_I2S_ABRI_M_18,102.1_I2B_ABRI_M_15,103.1_I2R_2016_M_18,103.1_I2E_2016_M_21&format=csv`](http://apis.datos.gob.ar/series/api/series/?ids=103.1_I2N_2016_M_15,101.1_I2NG_2016_M_22,102.1_I2S_ABRI_M_18,102.1_I2B_ABRI_M_15,103.1_I2R_2016_M_18,103.1_I2E_2016_M_21&format=csv)

## Filtrar por fechas

Los parámetros `start_date` y `end_date` permiten limitar una consulta a todos aquellos valores posteriores o anteriores (respectivamente) a una fecha determinada.

!!! note "[Tipo de cambio desde Enero de 2016](http://datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&start_date=2016-01)"

    [`https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&start_date=2016-01&limit=1000&format=csv`](https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&start_date=2016-01&limit=1000&format=csv)

!!! note "[Tipo de cambio hasta Diciembre de 2016](http://datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&end_date=2016-12)"

    [`https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&end_date=2016-12&format=csv`](https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&end_date=2016-12&format=csv)

!!! note "[Tipo de cambio desde Enero de 2016 hasta Diciembre de 2016](http://datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&start_date=2016-01&end_date=2016-12)"

    [`https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&start_date=2016-01&end_date=2016-12&format=csv`](https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&start_date=2016-01&end_date=2016-12&format=csv)

## Cambiar la agregación temporal

Por default, las series se muestran en la frecuencia más alta posible (esta es, la frecuencia más baja de todas las series consultadas a la vez). El parámetro `collapse` permite elegir una frecuencia más baja que esta.

!!! note "[Índice de Tipo de Cambio Real Multilateral, China y Brasil. Valores mensuales promediados por trimestre.](http://datos.gob.ar/series/api/series/?ids=116.3_TCRMA_0_M_36,116.3_TCRC_0_M_22,116.3_TCRB_0_M_23&collapse=quarter)"

    [`http://apis.datos.gob.ar/series/api/series/?limit=1000&collapse=quarter&ids=116.3_TCRMA_0_M_36,116.3_TCRC_0_M_22,116.3_TCRB_0_M_23&format=csv`](http://apis.datos.gob.ar/series/api/series/?limit=1000&collapse=quarter&ids=116.3_TCRMA_0_M_36,116.3_TCRC_0_M_22,116.3_TCRB_0_M_23&format=csv)

## Cambiar la función de agregación temporal

Por default, cuando la API hace agregaciones temporales (ie. convertir una serie mensual en trimestral) hace un **promedio de los valores de cada período**.

Esta función de agregación se puede cambiar para toda la consulta con el parámetro `collapse_aggregation`, o para cada serie en particular (suma, máximo, mínimo, etc.).

!!! note "[Tipo de cambio. Valores diarios a cierre de cada mes.](http://datos.gob.ar/series/api/series/?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=end_of_period)"

    [`https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=end_of_period&format=csv`](https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=end_of_period&format=csv)

!!! note "[Tipo de cambio. Valores diarios mínimo, promedio, máximo y cierre de cada mes.](http://datos.gob.ar/series/api/series/?ids=168.1_T_CAMBIOR_D_0_0_26:min,168.1_T_CAMBIOR_D_0_0_26:avg,168.1_T_CAMBIOR_D_0_0_26:max,168.1_T_CAMBIOR_D_0_0_26:end_of_period&collapse=month)"

    [`https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:min,168.1_T_CAMBIOR_D_0_0_26:avg,168.1_T_CAMBIOR_D_0_0_26:max,168.1_T_CAMBIOR_D_0_0_26:end_of_period&collapse=month&format=csv&limit=1000`](https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:min,168.1_T_CAMBIOR_D_0_0_26:avg,168.1_T_CAMBIOR_D_0_0_26:max,168.1_T_CAMBIOR_D_0_0_26:end_of_period&collapse=month&format=csv&limit=1000)

## Aplicar transformaciones

Las series de pueden transformar en otras unidades (variación porcentual, variación interanual, etc.) en forma individual o conjunta, usando el parámetro `representation_mode`.

!!! note "[Tipo de cambio, IPC núcleo e IPC nivel general desde Enero de 2016. Variación porcentual de valores mensuales, respecto del período anterior.](http://datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01&representation_mode=percent_change)"

    [`https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01&representation_mode=percent_change`](https://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01&representation_mode=percent_change)

!!! note "[IPC núcleo, IPC núcleo (variación porcentual período a período) e IPC núcleo (variación porcentual interanual) desde Enero de 2016. Valores mensuales.](http://datos.gob.ar/series/api/series/?ids=103.1_I2N_2016_M_15,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_15:percent_change_a_year_ago&start_date=2016-01)"
    *Nota: series con unidades de diferentes escalas, pueden ser difíciles de visualizar en un mismo gráfico.*

    [`https://apis.datos.gob.ar/series/api/series?ids=103.1_I2N_2016_M_15,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_15:percent_change_a_year_ago&start_date=2016-01&format=csv&limit=1000`](https://apis.datos.gob.ar/series/api/series?ids=103.1_I2N_2016_M_15,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_15:percent_change_a_year_ago&start_date=2016-01&format=csv&limit=1000)


## Aplicar transformaciones y cambiar la función de agregación temporal en series individuales, a la vez

Es posible aplicar a las series individuales **tanto una transformación como una función de agregación particular a la vez**.

En todos los casos, siempre se aplica **primero la función de agregación** y **luego la transformación**.

!!! note "[Tipo de cambio. Variación porcentual de valores diarios a cierre de cada mes, respecto del período anterior.](http://datos.gob.ar/series/api/series/?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period:percent_change&collapse=month)"

    [`http://apis.datos.gob.ar/series/api/series/?limit=1000&collapse=month&ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period:percent_change&format=csv`](http://apis.datos.gob.ar/series/api/series/?limit=1000&collapse=month&ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period:percent_change&format=csv)
