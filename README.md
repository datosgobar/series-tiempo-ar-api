# API de Series de Tiempo

[![Coverage Status](https://coveralls.io/repos/github/datosgobar/series-tiempo-ar-api/badge.svg?branch=master)](https://coveralls.io/github/datosgobar/series-tiempo-ar-api?branch=master)
[![Build Status](https://travis-ci.org/datosgobar/series-tiempo-ar-api.svg?branch=master)](https://travis-ci.org/datosgobar/series-tiempo-ar-api)
[![GitHub tag](https://img.shields.io/github/tag/datosgobar/series-tiempo-ar-api.svg)]()

Aplicación distribuible de la API de Series de Tiempo del [Paquete de Apertura de Datos de la República Argentina](http://paquete-apertura-datos.readthedocs.io/es/stable/).

* Versión python: 3.6
* Licencia: MIT license
* Release status: `beta`
* Documentación: [https://series-tiempo-ar-api.readthedocs.io](https://series-tiempo-ar-api.readthedocs.io)

## Instalación

Ver documentación de [instalación de la aplicación](docs/developers/development.md).

## Uso rápido

*Tipo de cambio, índice de precios núcleo (variación porcentual) e índice de precios nivel general (variación porcentual) desde Enero de 2016, en valores mensuales*

```
/series/?ids=138.1_PAPDE_0_M_41,103.1_I2N_2016_M_15:percent_change,103.1_I2N_2016_M_19:percent_change&collapse=month&format=csv&start_date=2016-01-01
```

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

Ver [documentación completa](https://datosgobar.github.io/series-tiempo-ar-api/)

## ¿Dónde encontrar los ids y otros metadatos de las series?

En http://www.datos.gob.ar podés encontrar la [base completa de series de tiempo](http://datos.gob.ar/dataset/base-series-tiempo-administracion-publica-nacional) y [descargar la lista de series](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.2/download/series-tiempo-metadatos.csv) disponibles para buscar cuáles consultar a la API.

También podés descargarte de ahí [todos los valores de la base completa](http://infra.datos.gob.ar/catalog/modernizacion/dataset/1/distribution/1.3/download/series-tiempo-valores.csv), en lugar de usar la API.

## Términos y condiciones de uso

La aplicación se publica actualmente como una versión `beta`. Ver detalle del [acuerdo de nivel de servicio]() (*TODO: escribir versión inicial de SLA*).

Tanto las funcionalidades e interfaz de la API como la arquitectura interna podrían sufrir modificaciones significativas en las próximas versiones.

Todo el código e instrucciones de instalación se publican actualmente sin condiciones de uso más que la cita de la fuente, y sin garantías ni soporte por parte del equipo de [Datos Argentina](datosgobar.github.io) para cualquier actor gubernamental, civil o privado que quiera instalar su propio servicio web de series de tiempo.

Se aclara al usuario desarrollador que todo el modelo de datos y metadatos, así como la arquitectura de la aplicación, están estrechamente basados en la [versión 1.1 del Perfil de Metadatos](http://paquete-apertura-datos.readthedocs.io/es/0.2.0/guia_metadatos.html) de la Política de Apertura de Datos de la Administración Pública Nacional de Argentina.

## Contacto

Te invitamos a [crearnos un issue](https://github.com/datosgobar/series-tiempo-ar-api/issues/new?labels=pedido-comunidad) en caso de que encuentres algún bug o tengas feedback de alguna parte de `series-tiempo-ar-api` o sobre el servicio web.

Para todo lo demás, podés mandarnos tu comentario o consulta a [datos@modernizacion.gob.ar](mailto:datos@modernizacion.gob.ar).




