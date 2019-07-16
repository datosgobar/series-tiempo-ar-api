# Referencia API: search

Recurso: `/validate`

El recurso `/validate` permite validar distribuciones de series de tiempo para determinar si están listas a ser cargadas en el servicio. Es una herramienta de utilidad para publicadores, es una manera de asegurarse que los datos están en el formato esperado por la API.


Se utiliza a través de una llamada de tipo POST (por ejemplo con `curl`):

```bash

curl POST $API_URL/series/api/validate -H 'Content-Type: application/json' -d '
{
"catalog_url": "http://infra.datos.gob.ar/catalog/sspm/data.json",
"distribution_id": "192.1" 
}'
```

Respuesta ejemplo:

```bash
{
    "catalog_url": "http://infra.datos.gob.ar/catalog/sspm/data.json",
    "distribution_id": "192.1",
    "found_issues": 2,
    "detail": [
        "Datos inconsistentes en la distribución 192.1: Comienzo '1881-01-01 00:00:00' / Fin '2009-01-01 00:00:00' / Frecuencia 'R/P3M' / Fechas '513' / Valores '129'",
        "Campo subtotal_agricola_60 faltante en la distribución 192.1"
    ]
}
```

Acepta dos parámetros, ambos obligatorios:

- `catalog_url`: URL del catálogo en donde se encuentra la distribución a validar
- `distribution_id`: `identifier` de la distribución a validar.

Ante cualquier error de parámetros faltantes o inválidos, devuelve una respuesta con código 400.
