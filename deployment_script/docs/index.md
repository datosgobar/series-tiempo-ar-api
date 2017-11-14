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

Ver la documentación específica [aquí](setup.md)


## Configuraciones

- [Elasticsearch](elasticsearch.md)
- [Redis](redis.md)
- [Workers](workers.md)


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

Ver la documentacion de [idea](idea.md) y [features](features.md)
