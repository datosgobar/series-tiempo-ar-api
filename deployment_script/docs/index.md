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

### Usuario para ansible

Si el usuario require _contraseña_ para usar comandos con `sudo`, previamente debemos correr el siguiente comando:
`export ANSIBLE_BECOME_ASK_PASS=true`. Esto hará que ansible nos pregunte *una sola vez* por esta contraseña.


## Requerimientos

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](http://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

## Setup un nuevo ambiente

Ver la documentación específica [aquí](docs/setup.md)


## Configuraciones

Para configurar la cantidad de memoria usada por elasticsearch, podemos configurarlo para todas las máquinas o por host.
Podemos agregar el archivo "inventories/staging/group_vars/es.yml" para configurar a todos los elasticsearch, o
podemos usar el archivo "inventories/staging/host_vars/-nombre-del-host-.yml" para un host sólo.


### Configuración de "binding"

Por default se configurará la IP que se usa para acceder al server (Recordamos que se asumen IP privadas).
Para configurarlas con valores fijos, basta agregar las siguientes variables (por host o grupo):

```yaml
---

es_bind_host: "127.0.0.1"
es_publish_host: "127.0.0.1"

```

### Configurar "Discovery" de nodos

Para desactivar el discovery de nodos (para cuando solo tenemos uno), podemos usar la siguiente variable:

```yaml
---

es_use_discovery: no
```

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
En el archivo "inventories/staging/group_vars/web/vars.yml" debemos agregar la siguiente parte:

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

En el archivo "inventories/staging/group_vars/web/vars.yml" agregar la configuración para conectar a redis desde los servidores o workers:

```yaml
---

# Reemplazar la IP por la correspondientes
default_redis_host: "192.168.35.30"
```

### Configuraciones

Para configurar la ip de "binding" de Redis manualmente, se debe usar la siguiente variable:

```yaml
---


redis_bind_host: "127.0.0.1"
```

## Post instalación

El script de deployment _no_ crea un super usuario en la aplicación.
Para hacerlo se requieren los siguientes pasos manuales *dentro del servidor*:

```
# Cambiar al usuario de la aplicacion
sudo su - devartis
cd /home/devartis/webapp

# Activar el virtualenv
. .venv/bin/activate
export DJANGO_SETTINGS_MODULE=conf.settings.production

# Correr el script
cd app/
python manage.py createsuperuser

```

## Vagrant & Tests

Se puede probar con [vagrant](http://www.vagrantup.com/) siguiendo los siguientes pasos:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
vagrant up --no-provision
# Incluyo el archivo de Vault como ejemplo
ansible-playbook -i inventories/vagrant/hosts --vault-password-file inventories/vagrant/vault_password.txt site.yml -v
```

Además con la variable de entorno "CHECKOUT_BRANCH" se puede configurar el branch que deseamos usar _dentro_ del servidor.

Para cambiar la cantidad de servidores de Elasticsearch debemos cambiar, dentro del archivo Vagranfile, la variable "ES_SERVER_COUNT" con un numero mayor a 1.


## Mas info

Ver la documentacion de [idea](docs/idea.md) y [features](docs/features.md)
