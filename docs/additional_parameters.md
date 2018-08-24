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

El parámetro `ids` permite la consulta simultánea de hasta 4 series a la vez, separadas por comas.

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15&format=csv`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15&format=csv
)

## Filtrar por fechas

Los parámetros `start_date` y `end_date` permiten limitar una consulta a todos aquellos valores posteriores o anteriores (respectivamente) a una fecha determinada.

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01
)

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general hasta Diciembre de 2016*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&end_date=2016-12-01`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&end_date=2016-12-01
)

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016, hasta Diciembre de 2016*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01&end_date=2016-12-01`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01&end_date=2016-12-01
)

## Cambiar la agregación temporal

Por default, las series se muestran en la frecuencia más alta posible (esta es, la frecuencia más baja de todas las series consultadas a la vez). El parámetro `collapse` permite elegir una frecuencia más baja.

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
)

## Cambiar la función de agregación temporal

Por default, cuando la API debe hacer agregaciones temporales (ie. convertir una serie mensual en trimestral) hace un promedio de los valores de cada período.

Esta función de agregación se puede cambiar para toda la consulta con el parámetro `collapse_aggregation`, o para cada serie en particular (suma, máximo, mínimo, etc.).

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general, en valores trimestrales a último valor del período*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter&collapse_aggregation=end_of_period`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter&collapse_aggregation=end_of_period
)

*Tipo de cambio (último valor del período), índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
)

## Aplicar transformaciones

Las series de pueden transformar en otras unidades (variación porcentual, variación interanual, etc.) en forma individual o conjunta, usando el parámetro `representation_mode`.

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016, en valores mensuales y variación porcentual*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01-01&representation_mode=percent_change`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01-01&representation_mode=percent_change
)

*Tipo de cambio, índice de precios núcleo (variación porcentual) e índice de precios nivel general (variación porcentual) desde Enero de 2016, en valores mensuales*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01
)

## Aplicar transformaciones y cambiar la función de agregación temporal en series individuales, a la vez

Es posible aplicar a las series individuales tanto una transformación como una función de agregación particular.

En todos los casos, siempre se aplica **primero la función de agregación** y **luego la transformación**.

*Tipo de cambio (variaciones porcentuales entre los últimos valores de cada período), índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

[`http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period:percent_change,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter`](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26:end_of_period:percent_change,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
)
