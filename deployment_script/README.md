# Series de tiempo AR - Deployment

Bienvenido a la documentación de "deployment" para Series de Tiempo AR

## Requerimientos

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](https://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

## Setup un nuevo ambiente

Para inicializar un nuevo ambiente, necesitaremos crear un nuevo sub-directorio en el directorio "inventories".
Como ejemplo usaremos "staging":

    mkdir -p inventories/stating/

Luego crearemos el inventario de las máquinas que ansible conocerá, podemos usar el archivo "inventories/vagrant/hosts" como base:

    web1

    [web]
    web1

En este ejemplo, le decimos a ansible que "web1" es una máquina, y ademas que pertenece al grupo "web".
Luego debemos decirle a ansible dónde encontrar esta máquina, para eso creamos el directorio "inventories/staging/host_vars".

    mkdir -p inventories/staging/host_vars

Luego dentro creamos un archivo en "inventories/staging/host_vars/web1.yml" donde le daremos a ansible algunas variables espeficicas para esa máquina:

```bash
ansible_host: 192.168.35.10
ansible_port: 22
```

Luego deberiamos ser capaces de correr el siguiente script:

```bash
./deploy.sh -i inventories/staging/hosts -p $DATABASE_USER -P $DATABASE_PASS -l $SSH_USER
```

Luego de finalzado, nuestro servidor debería contener toda la aplicación

*NOTA:* Si nuestro usuario require _password_ para usar comandos con `sudo`, previamente debemos correr el siguiente comando:
`export ANSIBLE_ASK_BECOME_PASS=true`.

## Vagrant & Tests

Se puede probar con [vagrant](https://www.vagrantup.com/) siguiendo los siguientes pasos:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
vagrant up --no-provision
./deploy.sh -p database_user -P database_pass -i inventories/vagrant/hosts -l vagrant
```