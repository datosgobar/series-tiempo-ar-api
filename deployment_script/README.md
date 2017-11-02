# Series de tiempo AR - Deployment

Bienvenido a la documentación de "deployment" para Series de Tiempo AR

## Consideraciones

### Sudo y las contraseñas

Si para los servidores a los que se van a acceder se necesita una contraseña para poder usar `sudo`,
_todos los usuario de ese servidor tiene que tener la misma contraseña_.
Esto se debe a que ansible _solamente_ deja usar 1 contraseña para sudo en todos los servidores.

### Punto de entrada

El script asume fuertemente que estamos accediendo a las máquinas desde _dentro de la misma red_.
O sea, todas las conecciones deben ser hechas a alguna IP del estilo "192.168.35.10".
Para que esto sea posible, se puede crear una máquina que sea solamente para correr el "deployment", _dentro de la misma red_.

## Requerimientos

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](http://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

## Setup un nuevo ambiente

Para inicializar un nuevo ambiente, necesitaremos crear un nuevo sub-directorio en el directorio "inventories".
Como ejemplo usaremos "staging":

    mkdir -p inventories/stating/

Luego crearemos el inventario de las máquinas que ansible conocerá, podemos usar el archivo "inventories/vagrant/hosts" como base:

    web1

    [web]
    web1

    [redis]
    web1
    
    [es]
    web1

    [api_cluster:children]
    web
    es
    redis

En este ejemplo, le decimos a ansible que "web1" es una máquina, y ademas que pertenece al grupo "web".
Además al pertenecer al grupo "es", ansible instalará `elasticsearch` en la máquina.


Luego debemos decirle a ansible dónde encontrar esta máquina, para eso creamos el directorio "inventories/staging/host_vars".

    mkdir -p inventories/staging/host_vars

Luego dentro creamos un archivo en "inventories/staging/host_vars/web1.yml" donde le daremos a ansible algunas variables espeficicas para esa máquina. En este ejemplo, especificamos la IP y el puerto ssh de la máquina.

```yaml
# Connection variables
ansible_host: 192.168.35.10
ansible_port: 22

```

Luego deberiamos ser capaces de correr el siguiente script:

```bash
./deploy.sh -i inventories/staging/hosts -p $DATABASE_USER -P $DATABASE_PASS -l $SSH_USER
```

Luego de finalzado, nuestro servidor debería contener toda la aplicación

*NOTA:* Si el usuario require _password_ para usar comandos con `sudo`, previamente debemos correr el siguiente comando:
`export ANSIBLE_BECOME_ASK_PASS=true`.

## Configuraciones

Para configurar la cantidad de memoria usada por elasticsearch, podemos configurarlo para todas las máquinas o por host.
Podemos agregar el archivo "inventories/staging/group_vars/es.yml" para configurar a todos los elasticsearch, o
podemos usar el archivo "inventories/staging/host_vars/-nombre-del-host-.yml" para un host sólo.


### Límite de memoria heap

El mismo debe tener estas variables (en este ejemplo limitamos a 1 gb):

```yaml
---

elastic_jvm_xmx: "1g"
elastic_jvm_xms: "1g"

```

### Desactivar swap

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
En el archivo "inventories/staging/group_vars/web.yml" debemos agregar la siguiente parte:

```yaml
# suponiendo que la IP de elasticsearch esta en 192.168.35.20.
es_urls: "http://192.168.35.20:9200/"
```

Si agregamos más servidores, simplementes agregamos las URLs separandolas por ",".

## Agregar un servidor de Redis

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

En el archivo "inventories/staging/group_vars/web.yml" agregar la configuración para conectar a redis desde los servidores o workers:

```yaml
---

# Reemplazar la IP por la correspondientes
default_redis_host: "192.168.35.30"
```



## Vagrant & Tests

Se puede probar con [vagrant](http://www.vagrantup.com/) siguiendo los siguientes pasos:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
vagrant up --provision
```

Además con la variable de entorno "CHECKOUT_BRANCH" se puede configurar el branch que deseamos usar _dentro_ del servidor.

Para cambiar la cantidad de servidores de Elasticsearch debemos cambiar, dentro del archivo Vagranfile, la variable "ES_SERVER_COUNT" con un numero mayor a 1.
