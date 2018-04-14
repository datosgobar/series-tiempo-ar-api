# API de Series de Tiempo de la República Argentina

Documentación de la API de Series de Tiempo del [Paquete de Apertura de Datos de la República Argentina](http://paquete-apertura-datos.readthedocs.io/es/stable/).

Esta API expone métodos para consultar series de tiempo abiertas por organismos que cumplen con el Perfil de Metadatos de la Política de Apertura de Datos de la Administración Pública Nacional.

La aplicación se publica actualmente como una versión `beta`. Tanto las funcionalidades e interfaz de la API como la arquitectura interna podrían sufrir modificaciones significativas en las próximas versiones.

El uso está sujeto a restricciones y cuotas, para preservar la estabilidad de la infraestructura.

* **Descargar lista de series**: [CSV](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.2/download/series-tiempo-metadatos.csv) - [XLSX](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.6/download/series-tiempo-metadatos.xlsx) - [DTA](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.10/download/series-tiempo-metadatos.dta).
* **Descargar base completa**: [http://datos.gob.ar/dataset/base-series-tiempo-administracion-publica-nacional](http://datos.gob.ar/dataset/base-series-tiempo-administracion-publica-nacional).

Se alienta a los usuarios a [dejar comentarios, reportes de fallas o sugerencias](https://github.com/datosgobar/series-tiempo-ar-api/issues/new?labels=pedido-comunidad).

## Ejemplo de uso

*Tipo de cambio, índice de precios núcleo (variación porcentual) e índice de precios nivel general (variación porcentual) desde Enero de 2016, en valores mensuales*

```md
http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01
```
[Descargar](http://apis.datos.gob.ar/series/api/series?ids=168.1_T_CAMBIOR_D_0_0_26,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01)

<table>
<tr><td>indice_tiempo</td><td>pesos_argentinos_por_dolar_estadounidense</td><td>ipc_2016_nucleo</td><td>ipc_2016_nivgeneral</td></tr>
<tr><td>2016-01-01</td><td>13.6099238</td><td></td><td></td></tr>
<tr><td>2016-02-01</td><td>14.7951857</td><td></td><td></td></tr>
<tr><td>2016-03-01</td><td>14.8990696</td><td></td><td></td></tr>
<tr><td>2016-04-01</td><td>14.3879762</td><td></td><td></td></tr>
<tr><td>2016-05-01</td><td>14.1183   </td><td>0.0265777</td><td>0.0419337</td></tr>
<tr><td>2016-06-01</td><td>14.1542409</td><td>0.0301247</td><td>0.0307591</td></tr>
<tr><td>2016-07-01</td><td>14.8882952</td><td>0.0187154</td><td>0.0204675</td></tr>
<tr><td>2016-08-01</td><td>14.8339304</td><td>0.0165157</td><td>0.0020196</td></tr>
<tr><td>2016-09-01</td><td>15.1174273</td><td>0.0154869</td><td>0.0114914</td></tr>
<tr><td>2016-10-01</td><td>15.1745429</td><td>0.0179986</td><td>0.0235933</td></tr>
<tr><td>2016-11-01</td><td>15.3529636</td><td>0.0171879</td><td>0.0161842</td></tr>
<tr><td>2016-12-01</td><td>15.8815   </td><td>0.0171243</td><td>0.0119757</td></tr>
<tr><td>2017-01-01</td><td>15.9102773</td><td>0.013389 </td><td>0.01313</td></tr>
<tr><td>2017-02-01</td><td>15.580245 </td><td>0.0184608</td><td>0.0246316</td></tr>
<tr><td>2017-03-01</td><td>15.5240391</td><td>0.0182095</td><td>0.0236416</td></tr>
<tr><td>2017-04-01</td><td>15.33552  </td><td>0.0229158</td><td>0.0263366</td></tr>
<tr><td>2017-05-01</td><td>15.7173087</td><td>0.0160246</td><td>0.0128313</td></tr>
<tr><td>2017-06-01</td><td>16.1231909</td><td>0.0152262</td><td>0.0138837</td></tr>
<tr><td>2017-07-01</td><td>17.1859524</td><td>0.0176384</td><td>0.0171937</td></tr>
<tr><td>2017-08-01</td><td>17.414913 </td><td>0.0150374</td><td>0.0147753</td></tr>
<tr><td>2017-09-01</td><td>17.2411857</td><td>0.017578 </td><td>0.0204363</td></tr>
<tr><td>2017-10-01</td><td>17.4550318</td><td></td><td></td></tr>
</table>

[Descargar ejemplo](https://github.com/datosgobar/series-tiempo-ar-api/raw/master/docs/assets/data-example-1.csv)

