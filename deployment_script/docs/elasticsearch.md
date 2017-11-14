# Elasticsearch

Para configurar la cantidad de memoria usada por elasticsearch, podemos configurarlo para todas las máquinas o por host.
Podemos agregar el archivo "inventories/staging/group_vars/es.yml" para configurar a todos los elasticsearch, o
podemos usar el archivo "inventories/staging/host_vars/-nombre-del-host-.yml" para un host sólo.


## Configuración de "binding"

Por default se configurará la IP que se usa para acceder al server (Recordamos que se asumen IP privadas).
Para configurarlas con valores fijos, basta agregar las siguientes variables (por host o grupo):

```yaml
---

es_bind_host: "127.0.0.1"
es_publish_host: "127.0.0.1"

```

## Configurar "Discovery" de nodos

Para desactivar el discovery de nodos (para cuando solo tenemos uno), podemos usar la siguiente variable:

```yaml
---

es_use_discovery: no
```

## Límite de memoria heap

El mismo debe tener estas variables (en este ejemplo limitamos a 1 gb):

```yaml
---

elastic_jvm_xmx: "1g"
elastic_jvm_xms: "1g"

```

## Desactivar swap

```yaml
---

# otras variables ...

off_swap: yes

```

## Agregar mas servidores para elasticsearch

Para agregar mas servidores con elasticsearch, debemos seguir los siguientes pasos:

Agregar un nuevo servidor en el inventario (en este caso, "es1") y ponerlo bajo el grupo "es":

    web1
    es1

    [web]
    web1

    [redis]
    web1

    [es]
    es1

    [api_cluster:children]
    web
    es
    redis

Luego debemos crear el archivo "inventories/staging/host_vars/es1.yml" con la configuración de acceso:


```yaml
# Connection variables
ansible_host: 192.168.35.20
ansible_port: 22

```

Luego debemos configurar todos los servidores "web" para que conozcan a los servidores de elasticsearch.
En el archivo "inventories/staging/group_vars/web/vars.yml" debemos agregar la siguiente parte:

```yaml
# suponiendo que la IP de elasticsearch esta en 192.168.35.20.
es_urls: "http://192.168.35.20:9200/"
```

Si agregamos más servidores, simplementes agregamos las URLs separandolas por ",".
