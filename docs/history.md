# Historial de versiones

## 1.22.0 - 2019/06/03

- Bugfix a consultas que devolvían datos vacíos cuando se pedía una serie con `collapse_aggregation` definido y sin `collapse`.

## 1.21.0 - 2019/05/15

- Cambios en la rutina de indexación de metadatos para hacer ciertos campos no obligatorios (`themeTaxonomy` de un catálogo fuente)
- La tabla de errores del reporte de indexación ahora viene ordenada según el ID del catálogo, y luego el ID de la distribución errónea


## 1.20.0 - 2019/05/13

- Validaciones adicionales en indexación de datos relacionadas con encoding de archivos en latin1
- Tabla de errores de distribuciones en reporte de indexación

## 1.19.0

- Fix de regresión de lectura de dataset identifiers durante la indexación de datos a Elasticsearch

## 1.18.0

- Fixes en indexación de distribuciones, no se verifica el certificado de SSL (necesario para obtener datos de algunos publicadores)
- Fix a lectura de series marcadas como no presentes

## 1.17.0

- Cambio caracter separador en /search: de ',' -> '||' (dos caracteres)

## 1.16.0

- Muestro ID de catalogos en reportes individuales
- Mejoras de manejo de errores de tareas asincronicas

## 1.15.0

- Bump de versión de django_datajsonar a 0.2.0, y adaptando la base de código para ser compatible con dicha versión
- Bugfix de indexación de metadatos: ahora se indexan todas las series _disponibles_ en vez de las _disponibles sin error_

## 1.14.0

- Bump de versión de django_datjasonar a 0.1.22
- Bugfix en cálculo de metadatos enriquecidos: ahora se calculan en todas las indexaciones, y no sólo cuando una distribución es actualizada

## 1.13.2

- Fix a mails no utilizando el campo from_email de la configuración dinámica.

## 1.13.1

- Fix a mails de test de integración mandandose múltiplies veces, y ocasionalmente con un attachment vacío
- Bump de versión micro de django_datajsonar
- Fix al callable_str de RunIntegrationTaskAdmin incorrecto

## 1.13.0

- Parametrización del índice de tiempo: no es más necesario utilizar un índice de tiempo con nombre `indice_tiempo` para indexar distribuciones
- Cambios de respuesta: percent_change cambia su nombre _verbose_ a `Variación porcentual período anterior`
- Validaciones adicionales en generación de dumps CSV y SQL

## 1.12.1

- Revert al uso de metadatos de consultas en el endpoint de búsqueda
- Revert al conteo de series en cada filtro de metadatos.
- Nuevo parámetro para `/search`: `aggregations` muestra el conteo de series relevantes para la búsqueda dada, desagregadas según los varios filtros posibles

## 1.12.0

- Bugfixes en indexación y respuesta de API series (#471, #473, #474)
- Administración de unidades de series, con atributo de si son porcentuales
- Conteo de series en cada filtro de metadatos
- Actualización de validaciones de series durante la indexación

## 1.11.0

Metadatos de consultas de las series: rutina de cálculo diaria, uso en dumps y en resultados de búsqueda de series

## 1.10.0

- Nuevos metadatos de series: `representation_mode` y `representation_mode_units`
- Borrado del croneado de tareas usado para metadatos, analytics y test de integración. Su funcionalidad quedó deprecada
por `Synchronizer` de `django_datajsonar`.

## 1.9.0

- Bump de la versión de `django_datajsonar` a 0.1.17, con mejoras de UX de Synchronizers
- Bump de la versión de `series-tiempo-ar` a 0.2.1, con una validación adicional para permitir distribuciones con series vacías, hasta cierta proporción.
- Agregados nuevos metadatos de series (`metadata=full` o `metadata=only`): `max_value`, `min_value`, `average`

## 1.8.0

- Integración con django_datajsonar: Uso de Synchronizers y Stages para correr
tareas asincrónicas de manera ordenada

## 1.7.0

- Optimizaciones de performance en dumps CSV 
- Indexación de datos: siempre se reindexan completamente las distribuciones (_refresh_)
- Test de integración y consistencia de los datos, a correr después de la indexación diaria.
- Bugfix de series sin datos cuando eran pedidas en un solo request
- Traducción parcial del panel de administración a español

## 1.6.0

Release con herramientas de administración para "refrescar" distribuciones de datos inconsistentes con su fuente.

## 1.5.1
Correcciones a dumps:

- Header faltante en hojas adicionales en dump XLSX
- Columnas y nombres de una tabla de dumps SQL
- Bugfix de generación de dump global XLSX
Mejoras de organización en el admin de django

## 1.5.0

- Nuevo parámetro `last`. Ver [documentación](https://series-tiempo-ar-api.readthedocs.io/es/latest/)
- Permito trailing slashes en URLs de descarga de dumps

## 1.4.3

- Fix de estabilidad de generación de dumps en general.

## 1.4.2

- Fix a tasks asincrónicas de dumps no corriendo correctamente cuando son generadas desde el admin

## 1.4.0

- Orden a filas de dump de metadatos
- No es más necesario setear dataset_identifier en distributciones para ser indexadas
- Se permiten csvs de distribuciones con encoding distinto a utf-8

## 1.3.3

- Callables de rqscheduler para dumps CSV y XLSX.

## 1.3.2

- Optimizaciones de memoria de generación dumps xlsx

## 1.3.1 

- Pequeño release con un fix a parseo de URLs de descarga de distribuciones


## 1.3.0 hotfix 2

- Hotfix para servir files de minio desde una ruta interna de la aplicación

## 1.3.0 hotfix 1

- Hotfixes de logging de dump

## 1.3.0

- Nueva generación de dumps en CSV, usando los datos cargados en postgres, y generando dumps individuales por catálogo.
- Borrado de datos en el endpoint de /search/ cuando una serie se borra de la base de datos

## 1.2.1

- Refactor e integración de generación de dumps de la base de datos de series de tiempo, para utilizar postgres en vez de Elasticsearch e integrar los archivos al filesystem distribuido

## 1.2.0

- Adopción de [semver](https://semver.org/) como sistema de versionado
- File system distribuido (minio)
- Optimizaciones en la UI del admin
- Display de mensajes de error en reportes de indexación

## 1.1.8

- Correcciones en importado de analytics para adaptarse a la nueva API paginada con cursor en api mgmt

## 1.1.7

- Cambio de nombres de respuesta de metadatos.
- Fixes de usabilidad del admin relacionado a administradores de nodos.
- Bugfixes en respuesta de /series


## 1.1.6

- Se aumenta el límite de series máximas por request a 40
- Revisión de nombres y agregado de metadatos en la respuesta de /series
- Cambio de nombre de parámetro de /search: offset -> start para consistencia con /series

## 1.1.5

- Análisis y tokenización de texto para la búsqueda de metadatos en /search. Permite reconocer palabras sin acento, entre otras cosas.
- Muestra de metadatos enriquecidos de las series pedidas en /series, cuando se pide la respuesta con metadata=full o metadata=only. Actualmente todos los valores devueltos son de tipo string, sujeto a cambios a futuro.

## 1.1.4

- Modificación de la respuesta de metadatos en search/: se agregan campos dataset.theme, dataset.source y
field.units. Además se cambia la respuesta de field.periodicity de formato legible por humanos a ISO8601

## 1.1.3

- Actualizaciones de django_datajsonar
- Se agregan aliases de catálogos para metadatos. Se puede configurar un alias para los filtros catalog_id que sea equivalente a filtrar por uno o más catálogos.

## 1.1.2

- Funcionalidades de importado histórico de analytics, y ampliación de los datos guardados de cada query

## 1.1.1

- Validación de catálogos leídos al generar reporte
- Fixes a los valores de reportes
- Fix de metadatos enriquecidos no mostrándose bien en /search/

## 1.1.0

- Nuevo formato de respuesta de metadatos tanto en /series como en /search
- Mejoras en visualizaciones del admin de django

## 1.0.18

- Mejoras al endpoint de búsqueda: nuevo parámetro catalog_id
- Mejoras al indexado de metadatos
- Configuración de importado de analytics desde un API gateway

## 1.0.17

Se pasa a usar `django_datajsonar` como dependencia directa para manejar las entidades procesadas de data.json de los nodos

## 1.0.16-1

Actualización de dependencias pydatajson==0.4.12

## 1.0.16

Actualización de validaciones para indexación

## 1.0.15

Release con:

- Resumen de reporte de indexación
- Detalle de cada entidad indexada como archivos adjuntos en el reporte
- Reimplementación de aggregations max y min
- Fechas en el dump de analytics se exportan en horario local

## 1.0.14

Mejoras al formato del reporte de indexación, junto con mensajes de error más descriptivos

## 1.0.13

Hotfix con fixes a comportamiento erróneo en queries de dos series iguales con distinto modo de representación + uso de caracter decimal no default

## 1.0.12

Release con:

- Permite generar reportes de indexación individuales por nodo
- Fixes a valores de los reportes (datasets actualizados, no actualizados)
- Mejoras de performance de la indexación de metadatos

## 1.0.11

Generación de reporte de indexación completo: Nuevos fields para catálogos, datasets, distribuciones y series.

## 1.0.10

- Mejoras en la generación de reportes de indexación, con más campos reportados.

## 1.0.9

- Mostrado de versión en la página principal del admin de Django
- Mejora del proceso de indexación y persistencia de las métricas obtenidas
- Bugfix para permitir que las series de tiempo puedan cambiar de distribución dentro de un mismo catálogo

## 1.0.8

Bugfixes:

- Correcciones a llamadas de series múltiples en orden descendiente
- Permito la exportación correcta de analytics a CSV en volúmenes grandes
- Correcciones a guardados de analytics erróneos

## 1.0.7

Endpoint de búsqueda de series: `/search`

## 1.0.6

Fixes a herramientas de administración:

- No se indexan metadatos de series y distribuciones pertenecientes a catálogos no marcados como indexables
- Finalización automática de la tarea de indexación si no hay datasets marcados como indexable
- Arreglos a borrados de croneado de tareas de indexación

## 1.0.3
Herramientas de administración:

- Configuración de que nodos y datasets se deben indexar
- Configuración del croneado de la tarea de indexación
- Generación de reportes de resultado de indexación por mail a los administradores 

## 1.0.0
Release inicial
