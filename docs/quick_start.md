# Comienzo rápido

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

## Aplicar transformaciones

*Tipo de cambio, índice de precios núcleo e índice de precios nivel general desde Enero de 2016, en valores mensuales y variación porcentual*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15,103.1_I2N_2016_M_19&collapse=month&format=csv&start_date=2016-01-01&representation_mode=percent_change
```

*Tipo de cambio, índice de precios núcleo (variación porcentual) e índice de precios nivel general (variación porcentual) desde Enero de 2016, en valores mensuales*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01
```
