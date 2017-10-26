# Series de tiempo AR - Deployment

Bienvenido a la documentación de "deployment" para Series de Tiempo AR

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
    
    [es]
    web1

    [cluster:children]
    web
    es

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
podemos usar el archivo "inventories/staging/host_vars/<nombre-de-host>.yml" para un host sólo.
El mismo debe tener estas variables (en este ejemplo limitamos a 512 mb):

```yaml
---

elastic_jvm_xmx: "1g"
elastic_jvm_xms: "1g"
```

## Agregar mas servidores para elasticsearch

Para agregar mas servidores con elasticsearch, debemos seguir los siguientes pasos:

Agregar un nuevo servidor en el inventario (en este caso, "es1") y ponerlo bajo el grupo "es":

    web1
    es1

    [web]
    web1

    [es]
    es1

    [cluster:children]
    web
    es

Luego debemos crear el archivo "inventories/staging/host_vars/es1.yml" con la configuración de acceso:


```yaml
# Connection variables
ansible_host: 192.168.35.20
ansible_port: 22

```

## Vagrant & Tests

Se puede probar con [vagrant](http://www.vagrantup.com/) siguiendo los siguientes pasos:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
vagrant up --no-provision
./deploy.sh -p database_user -P database_pass -i inventories/vagrant/hosts -l vagrant
```
