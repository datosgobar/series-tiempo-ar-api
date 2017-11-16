# Inicialización de un nuevo ambiente


Para inicializar un nuevo ambiente, necesitaremos crear un nuevo sub-directorio en el directorio "inventories".
Como ejemplo usaremos "staging":

    mkdir -p inventories/stating/

Luego crearemos el inventario de las máquinas que ansible conocerá, podemos usar el archivo "inventories/vagrant/hosts" como base:

```
web1

[web]
web1

[rqworker]
web1

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

En este ejemplo, le decimos a ansible que "web1" es una máquina.
Además que pertenece a los grupos "web" (indica que debe descargarse correrse un webserver y la base de datos),
"rqworker" (indica que se correrá un worker en esa maquina), "es" (que indica que debe instalarse Elasticsearch)
y "redis" (que indica que se instalará redis-server)


Luego debemos decirle a ansible dónde encontrar esta máquina, para eso creamos el directorio "inventories/staging/host_vars".

    mkdir -p inventories/staging/host_vars

Luego dentro creamos un archivo en "inventories/staging/host_vars/web1/vars.yml" donde le daremos a ansible algunas variables espeficicas para esa máquina. En este ejemplo, especificamos la IP y el puerto ssh de la máquina.

```yaml
# Variables de conección

# Podemos especificar aquí o para mejor seguridad en vault.yml
ansible_host: 192.168.35.10
ansible_port: 22

```

Luego agregamos las credenciales privadas y las encriptamos con [Ansible Vault](https://docs.ansible.com/ansible/2.4/vault.html)
Para esto creamos los archivos "inventories/staging/group_vars/web/vars.yml" y "inventories/staging/group_vars/web/vault.yml"

En el "vars.yml" ponemos el siguiente contenido:

```yaml
---
# vars.yml

postgresql_user: "{{  postgresql_user_vault }}"
postgresql_password: "{{ postgresql_password_vault }}"
```

Como vemos, estas variables hacen referencia a otras variables, las que se encontrarán en el archivo "vault.yml".
En este archivo debemos poner el valor real de las variables.

```yaml
---
# vault.yml

ansible_user: my_user
postgresql_user_vault: my_usuario_de_la_base_de_datos
postgresql_password_vault: my_pass_de_la_base_de_datos
```

Finalmente encriptamos las credenciales:

`ansible-vault encrypt inventories/staging/group_vars/web/vault.yml`

*Nota: Debemos guardar la contraseña que usemos en un lugar seguro.*

Luego deberiamos ser capaces de correr el siguiente script:

```bash

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

ansible-playbook site.yml -i "inventories/staging/hosts" -vv --ask-vault-pass
```

Luego de finalzado, nuestro servidor debería contener toda la aplicación
