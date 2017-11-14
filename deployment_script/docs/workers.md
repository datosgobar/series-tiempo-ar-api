# Agregar más Workers

En el ejemplo, se instalará redis en el mismo servidor que el servidor web.
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
