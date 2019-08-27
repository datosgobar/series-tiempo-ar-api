# Documentación de administración de la API

El proyecto se desdobla en varias aplicaciones, todas ellas con configuraciones particulares, accesibles desde el panel de administración `/admin` ("el admin").

## Tareas en segundo plano

La API cuenta con varias tareas que se corren en segundo plano: la lectura de datos de series de tiempo, la indexación de dichos datos al índice de Elasticsearch, la generación de dumps de la base entera, entre otras. Todas las tareas se pueden correr manualmente creando nuevos modelos de tipo "Corrida" desde el admin, por ejemplo, `Corridas de importación de analytics`, `Corridas de indexación de datos`. Dentro de los modelos se encuentran los logs de cada corrida.

## Programación de tareas

Las tareas se pueden programar como una cola a correrse de manera automática a través de los modelos `Synchronizer` de [`django_datajsonar`](https://github.com/datosgobar/django-datajsonar/). Consultar su documentación para más información. A continuación se deja un ejemplo de una secuencia de tareas. 

- `Read Datajson (corrida completa)`
- `Indexación de datos (sólo actualizados)`
- `Test de integración`
- `Reporte de indexación`
- `Indexación de metadatos`
- `Generación de dumps CSV`
- `Generación de dumps XLSX`
- `Generación de dumps SQL`
- `Generación de dumps DTA`

Esta programación de tareas se puede realizar creando o editando desde el admin los modelos `Synchronizer`.

Adicionalmente, se pueden programar corridas individuales utilizando el botón `Schedule Task` en las vistas individuales de los modelos de tipo "Corrida" mencionados anteriormente, pero es fuertemente recomendado utilizar Synchronizers por su funcionalidad más extensiva.

## Rutina de indexación de datos 

Dentro de la vista "Configuración de rutina de indexación" se puede configurar el timeout global dado para cada distribución (en segundos). Luego de este tiempo, la indexación de esa distribución será considerada como fallida. Esto es para evitar el bloqueo de recursos de procesamiento frente a tareas que están bloqueadas por alguna falla externa a la aplicación. Por defecto, este valor es **1000 segundos**.


## Analytics

Existe un módulo de la aplicación que se dedica a importar datos de uso de la aplicación desde una instanacia de [api-gateway](https://github.com/datosgobar/api-gateway). Se puede configurar a través de la vista "Configuración de importación de analytics" en el admin, a llenar con los campos relevantes de la instancia de API Gateway que querramos consultar, incluyendo ID de la API de series de tiempo en ese proyecto, y una api key. El campo `Last Cursor` es de uso interno y **no debería ser modificado**.

## Test de integración

Existe un módulo que, idealmente justo después de una indexación de datos, se encargue de testear la consistencia de los datos cargados en el índice de Elasticsearch con los datos originales. Para la generación del reporte en casos de errores, se pueden configurar usuarios destinatarios del email de error. en la vista "Configuración del test de integración", así como el endpoint de la misma API a utilizar en los repotes (la API no conoce su propio host name, y por lo tanto debe ser configurado manualmente).

Adicionalmente, en la vista anterior, también se puede configurar un _Timeout_ para la rutina del test, en el caso de que, por el volumen de los datos indexados, se requiera más tiempo para finalizar. Por defecto se le asignan **1000 segundos** de tiempo de ejecución a la rutina. Luego de ese tiempo, el test fallará. 

## Metadatos

Otra tarea programada es la indexación de metadatos de las series disponibles, para ser consultadas en el endpoint `/search`. La tarea debe ser corrida siempre después de la indexación de datos, para asegurar que ambos índices contengan datos consistentes entre ellos.

Dentro de la vista "Configuración de búsqueda de series por metadatos", se pueden configurar parámetros de _boosting_ sobre ciertos campos de metadatos, para ir ajustando los resultados de búsqueda. El formato JSON de los parámetros debe ser siempre respetado. A continuación se muestra el valor por defecto:

`{"description": {"boost": 1.5}, "dataset_title": {"boost": 1}, "dataset_source": {"boost": 1}, "dataset_description": {"boost": 1}}`

Así, el campo _description_ de las series tiene cierta relevancia adicional sobre los demás (1.5 vs 1).

Si se modifica el _boost_ de algún campo, no es necesario reindexar los datos para que el cambio tome efecto, se aplica en tiempo de búsqueda y no de indexación.

## Dumps

Existen cuatro tareas relacionadas a la generación de dumps de la base entera de series de tiempo. Son una tarea por cada formato disponible: CSV, XLSX, SQL, DTA. Cada tarea genera dumps _globales_, de la base entera, y también individuales por cada nodo. 

Existe una fuerte dependencia entre estas tareas: los dumps en CSV se generan a partir de lecturas a la base de datos para leer metadatos, y al file storage para leer los datos de cada serie. Los demás formatos se generan a partir del dump CSV. Por lo tanto el dump en CSV debe ser programado 3 horas antes que los demás.

Los dumps CSV y XLSX generan **4 distribuciones por catálogo**, Los dumps en SQLite un archivo único por catálogo con varias tablas, y los dumps en DTA 3 archivos, todos disponibles en un endpoint accesible al público. Los dumps generados tendrán los datos de todas las series disponibles por la API, es decir las series cuyos datos fueron indexados exitosamente.


## Unidades porcentuales y no porcentuales

Una vez cargadas e indexadas las series, en la vista de `Unidades de series` en el admin se pueden indicar cuales de las unidades se deberían interpretar como porcentuales. Por defecto todas las unidades existentes son tratadas como valores absolutos. Cuando una unidad se marque como porcentual, en la respuesta de metadatos de las series, el campo `ìs_percentage` pasará a valer `true` en todos los casos de consulta de series que estén representadas bajo esa unidad. El propósito de esta funcionalidad es para indicarle a los usuarios de manera más sencilla si los valores de una serie deberían ser tratados como porcentajes o no.
