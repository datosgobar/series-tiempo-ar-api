# Spike de series de tiempo y APIs

Spike de APIs de bases de datos de series de tiempo.
Es necesario tener configurada una instancia de Elasticsearch>=5.4 corriendo en localhost:9200.

## Iniciando ES

```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:5.5.0
docker run -p 9200:9200 -e "http.host=0.0.0.0" -e "transport.host=127.0.0.1" docker.elastic.co/elasticsearch/elasticsearch:5.5.0
```

Usar como credenciales elastic:changeme

Ver: https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html

### Carga de datos de muestra
Primero hay que crear el índice de indicadores (si no existe anteriormente):
`curl -XPUT "$ES_URL/indicators/`

Siguiente, se generan los mappings de las series a cargar:
```bash
curl -XPUT "$ES_URL/indicators/_mapping/oferta_global_pbi/?pretty" -H 'Content-Type: application/json' -d '
{
  "properties": {
    "timestamp":                    {"type": "date"},
    "value":                        {"type": "scaled_float", "scaling_factor": 10000000},
    "change":                       {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change":               {"type": "scaled_float", "scaling_factor": 10000000},
    "change_a_year_ago":            {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change_a_year_ago":    {"type": "scaled_float", "scaling_factor": 10000000}
  },
  "_all": {"enabled": false},
  "dynamic": "strict"
}'
```
```bash
curl -XPUT "$ES_URL/indicators/_mapping/demanda_global_ibif_total/?pretty" -H 'Content-Type: application/json' -d '
{
  "properties": {
    "timestamp":                    {"type": "date"},
    "value":                        {"type": "scaled_float", "scaling_factor": 10000000},
    "change":                       {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change":               {"type": "scaled_float", "scaling_factor": 10000000},
    "change_a_year_ago":            {"type": "scaled_float", "scaling_factor": 10000000},
    "percent_change_a_year_ago":    {"type": "scaled_float", "scaling_factor": 10000000}
  },
  "_all": {"enabled": false},
  "dynamic": "strict"
}'
```

Luego, cargamos los datos a partir del archivo `sample_data.json`. Desde el directorio raíz del proyecto:
```bash 
curl -XPOST "$ES_URL/_bulk?pretty" -H 'Content-Type: application/json' --data-binary "@samples/sample_data.json"
```


## Snippets de elastic search

Todos los scripts siguientes son versiones "In progress" para validar el funcionamiento de las herramientas.

### Creación de índices con sus tipos

Crea el índice `indicators` con dos tipos: `demanda_global_ibif_total` y `oferta_global_pbi`, cada uno con sus atributos.

```bash
curl -XPUT "$ES_URL/indicators?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "oferta_global_pbi": {
      "_all":       { "enabled": false  },
      "dynamic":      "strict",
      "properties": {
        "timestamp":                    { "type": "date" },
        "value":                        { "type": "scaled_float", "scaling_factor": 10000000 },
        "change":                       { "type": "scaled_float", "scaling_factor": 10000000 },
        "percent_change":               { "type": "scaled_float", "scaling_factor": 10000000 },
        "change_a_year_ago":            { "type": "scaled_float", "scaling_factor": 10000000 },
        "percent_change_a_year_ago":    { "type": "scaled_float", "scaling_factor": 10000000 }
      }
    },
    "demanda_global_ibif_total": {
      "_all":       { "enabled": false  },
      "dynamic":      "strict",
      "properties": {
        "timestamp":                    { "type": "date" },
        "value":                        { "type": "scaled_float", "scaling_factor": 10000000 },
        "change":                       { "type": "scaled_float", "scaling_factor": 10000000 },
        "percent_change":               { "type": "scaled_float", "scaling_factor": 10000000 },
        "change_a_year_ago":            { "type": "scaled_float", "scaling_factor": 10000000 },
        "percent_change_a_year_ago":    { "type": "scaled_float", "scaling_factor": 10000000 }
      }
    }
  }
}
'
```

### Ejemplo de average usando date histogram

Agrupa por año y devuelve el promedio del campo `value`.

```bash
curl -XGET "$ES_URL/indicators/oferta_global_pbi/_search?&pretty" -d '
{
 "size": 0,
 "aggs": {
   "average_value_by_year": {
     "date_histogram": {
       "field": "timestamp",
       "interval": "year"
     },
     "aggs": {
       "value": {
         "avg": {
           "field": "value"
         }
       }
     }
   }
 }
}
'
Add Comment
```

### Ejemplo de "valor de cierre" agrupando por año

Devuelve para cada año el campo `value` de la última medición (último trimestre)

```bash
curl -XGET "$ES_URL/indicators/oferta_global_pbi/_search?&pretty" -d '
{
 "size": 0,
 "aggs": {
   "last_value_by_year": {
     "date_histogram": {
       "field": "timestamp",
       "interval": "year"
     },
     "aggs": {
       "last": {
         "scripted_metric": {
           "init_script": "params._agg.last_date = -1; params._agg.value = 0;",
           "map_script": "if (doc.timestamp.value > params._agg.last_date) { params._agg.last_date = doc.timestamp.value; params._agg.value = doc.value.value; }",
           "reduce_script": "double value = -1; long last_date = 0; for (a in params._aggs) { if (a != null && a.last_date > last_date) { value = a.value; last_date = a.last_date; } } return value"

         }
       }
     }
   }
 }
}
'
Add Comment
```


## Ejemplo de uso de la API
Todas las operaciones se pueden combinar entre sí.
- Query simple de una serie:
`http://127.0.0.1:8000/search/oferta_global_pbi/`
- Cambio de agregación:
`http://127.0.0.1:8000/search/oferta_global_pbi/?field=percent_change`
- Cambio de intervalo (_collapse_):
`http://127.0.0.1:8000/search/oferta_global_pbi/?interval=quarter`
- Operación de proporción entre dos series:
`http://127.0.0.1:8000/search/oferta_global_pbi/?agg=proportion&series=demanda_global_ibif_total`
- Filtro por fechas (desde, hasta)
`http://127.0.0.1:8000/search/oferta_global_pbi/?from=2005&to=2010`
- Filtro hasta fecha de hoy:
`http://127.0.0.1:8000/search/oferta_global_pbi/?to=now`
- Operación de índice en base 100 en alguna fecha particular:
`http://127.0.0.1:8000/search/oferta_global_pbi/?agg=index&base=2005&interval=quarter&from=2004&to=2015`
Si no se completa la fecha, se asume que es el primer día del año especificado (en este caso, `2005-01-01`)
#### Fields disponibles:
`value`, `change`, `percent_change`, `change_a_year_ago`, `percent_change_a_year_ago`. Valor default: `value`

#### Operaciones/agregaciones disponibles:
`avg`, `sum`, `max`, `min`, `proportion`. Valor default: `avg`

#### Intervalos disponibles:
`year`, `quarter`. Valor default: `year`

### Generación de datos aleatorios
Correr `./manage.py generate_data`

Parámetros opcionales: 
- `--indicators`: Cantidad de series aleatorias a generar. Default: 1
- `--years`: Cantidad de datos a generar. Default: 100 
- `--interval`: Granularidad de los datos a generar. Acepta `month`, `year` o `quarter`. Default: `quarter`

## Arquitectura propuesta

Durante el desarrollo del spike pudimos comenzar a pensar en la arquitectura que tendrá la API basada en datos temporalizados y en evaluar tecnologías que nos permitirán atacar las funcionalidades a implementar.

![Arquitectura](https://github.com/datosgobar/spike-series-de-tiempo/raw/master/docs/imgs/APIs%20y%20TS%20-%20Arquitectura.png)

![Procesamiento de Requests](https://github.com/datosgobar/spike-series-de-tiempo/raw/master/docs/img/APIs%20y%20TS%20-%20Procesamiento de Request.png)
