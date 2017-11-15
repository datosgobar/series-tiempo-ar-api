# Agregar más Workers

## Pre requisito

Para el correcto funcionamiento de la aplicación, es necesario que *todas* las instancias de la aplicacion, ya se
servidores "web" o "workers" compartan la misma [SECRET_KEY](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY).
El script está configurado para generar una api _por instancia_ tanto web como worker. Esto haría que cada uno genere su propia key.

Para arreglar esto, debemos setear dos variables: "generate_django_secret_key" y "django_secret_key" a nivel del cluster.
Para esto agregamos la configuracion en `inventories/<ambiente>/group_vars/api_cluster/vars.yml` y en
`inventories/<ambiente>/group_vars/api_cluster/vault.yml`.

Para generar la key, podemos usar los siguientes comandos:

```bash
pip install django
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

```

Luego guardamos el *output* del último comando en el inventario, encriptándolo con ansible Vault.

Por ejemplo, en `vars.yml` usamos:

```yaml
---

generate_django_secret_key: no
django_secret_key: "{{ django_secret_key_vault }}"
```

Y en `vault.yml` usamos:

```

django_secret_key: <nuestra api key>
```

## Agregar más servidores

Para instalarlo en otro servidor, se pueden seguir los siguientes pasos:

1)

Agregar un "host" al inventario, en este ejemplo, "worker1".

```
web1
worker1

[web]
web1

[rqworker]
worker1

[es]
web1

[redis]
web1

[apps:children]
web
rqworker

[api_cluster:children]
web
rqworker
es
redis

```

Agregar el archivo "inventories/staging/host_vars/worker1.yml", para configurar cómo se accede a el mismo.

```yml
---

ansible_host: 192.168.35.40
ansible_port: 22
```

Además debemos agregar el siguiente archivo con el siguiente contenido.
En el archivo "inventories/staging/group_vars/rqworker.yml" poner:

```yml
---

run_migrations: no
```

Esto evitará que los workers intenten correr migraciones de la aplicación.


## Configuraciones

Para la cantidad de workers a levantar dentro del host, basta modificar la variable "worker_count" en "inventories/staging/host_vars/worker1.yml"
```yaml
---


worker_count: 2 # o más
```
