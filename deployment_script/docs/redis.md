# Agregar un servidor de Redis

En el ejemplo, se instalará redis en el mismo servidor que el servidor web.
Para instalarlo en otro servidor, se pueden seguir los siguientes pasos:

1)

Agregar un "host" al inventario, en este ejemplo, "redis1".  Agregar el archivo "inventories/staging/host_vars/redis1.yml", para
configurar cómo se accede a el mismo.

```
web1
es1
redis1

[web]
web1

[es]
es1

[redis]
redis1

[api_cluster:children]
web
es
redis
```

En el archivo "inventories/staging/group_vars/web/vars.yml" agregar la configuración para conectar a redis desde los servidores o workers:

```yaml
---

# Reemplazar la IP por la correspondientes
default_redis_host: "192.168.35.30"
```

## Configuraciones

Para configurar la ip de "binding" de Redis manualmente, se debe usar la siguiente variable:

```yaml
---


redis_bind_host: "127.0.0.1"
```
