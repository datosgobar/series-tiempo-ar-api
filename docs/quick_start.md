# Comienzo rápido

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Descargar una tabla con una o varias series](#descargar-una-tabla-con-una-o-varias-series)
- [Filtrar por fechas](#filtrar-por-fechas)
- [Cambiar la agregación temporal](#cambiar-la-agregaci%C3%B3n-temporal)
- [Cambiar la función de agregación temporal](#cambiar-la-funci%C3%B3n-de-agregaci%C3%B3n-temporal)
- [Aplicar transformaciones](#aplicar-transformaciones)
- [Aplicar transformaciones y cambiar la función de agregación temporal en series individuales, a la vez](#aplicar-transformaciones-y-cambiar-la-funci%C3%B3n-de-agregaci%C3%B3n-temporal-en-series-individuales-a-la-vez)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Descargar una tabla con una o varias series

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15&format=csv
```

## Filtrar por fechas

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01
```

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general hasta Diciembre de 2016*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&end_date=2016-12-01
```

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016, hasta Diciembre de 2016*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&start_date=2016-01-01&end_date=2016-12-01
```

## Cambiar la agregación temporal

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
```

## Cambiar la función de agregación temporal

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general, en valores trimestrales a último valor del período*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter&collapse_aggregation=end_of_period
```

*Tipo de cambio (último valor del período), índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

```
/series/?ids=138.1_PAPDE_0_M_41:end_of_period,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
```

## Aplicar transformaciones

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016, en valores mensuales y variación porcentual*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01-01&representation_mode=percent_change
```

*Tipo de cambio, índice de precios núcleo (variación porcentual) e índice de precios nivel general (variación porcentual) desde Enero de 2016, en valores mensuales*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01
```

## Aplicar transformaciones y cambiar la función de agregación temporal en series individuales, a la vez

*Tipo de cambio (variaciones porcentuales entre los últimos valores de cada período), índice de precios núcleo e índice de precios nivel general, en valores trimestrales*

```
/series/?ids=138.1_PAPDE_0_M_41:end_of_period:percent_change,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&format=csv&collapse=quarter
```
