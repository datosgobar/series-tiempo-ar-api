# Series de tiempo AR - Deployment

## Implementación

La implementación actual usa [ansible](https://www.ansible.com/) para provisionar la(s) máquiná(s).

### Base

Los servidores terminarán con las siguientes características:

- `python2` instalado, requerido por ansible
- `acl` como una utilidad requerida por ansible
- `python2`, `pip`, `virtualenv`, `pytohn-dev` para usar la aplicacion Django
- `vim`, `htop` tareas de administración remota.
- `git` como herramienta para obtener el código de la aplicación.
- Firewall
  - Sólo se permiten conecciones a los puertos `22, 80, 443` para el servidor web.
  - Sólo se permiten conecciones a los puertos  `22, 9200-9400` para el servidor de elasticsearch.
- Usuarios y grupos: Se crea un usuario sin privilegios llamado `devartis`.
- Estructura de la aplicación:
  - El código de la aplicación estará en `/home/devartis/webapp/` (APP_ROOT), junto con los logs, configuraciones y scripts.
  - `app/`: La aplicación propiamente dicha, clonada con GIT.
  - `sockets/`: cualquier socket usado por Gunicorn o PostgreSQL
  - `logs/`: Logs de la aplicación, ya sea Gunicorn, Nginx o PostgreSQL
  - `config/`: Configuración de la aplicación, como el `.env` usado.
  - `bins/`: Scripts útiles.

Estructura de archivos:

```
- /home/devartis/webapp/ # Root application directory
                - app/
                - sockets/
                - logs/
                - config/
                - bins/
```

### Postgres

- Instalar `postgres` y `postgres-contrib`.
- Instalar `python-psycopg2` requerido por ansible
- Crear el sub-directorio "postgres" en `sockets/`, `logs/`, `config/` y `bins/`
- Asegurarse que la base de datos sea creada y el usuario este presente.
- Asegurarse que postgreSQL inicie con el sistema.

### Aplicación Django


- La aplicación será clonada en `app/`
- Se crearán los directorios para `MEDIA` y `STATIC` en la aplicación.
- Se instalarán las dependencias mediante el comando: `pip install -r requirements.txt`.
- Se generarán los archivos estaticos con el comando `python manage.py collectstatic --noinput`.
- Se correrán las migraciones de la aplicación con `python manage.py migrate`.
- Se creará un link desde `config/app/env` a `config/setting/.env`.
- Estructura de archivos (Relativo a `/home/devartis/webapp/`)
  - `app/`: Código de la aplicación.
  - `.venv/`: "virtualenv" donde se isntalarán los requerimientos python de la aplicación
  - `config/app/`
    - `env`: Donde se guardaran las credenciales, según la especificación de [django-environ](https://pypi.python.org/pypi/django-environ).
    - `secret_key`: Un "secret token" generado en el primer deploy (Ver `roles/django_application/files/django_secret_key.py` para mas detalles).

### Gunicorn & nginx

- Agregar la configuración de **Gunicorn**.
- Agregar la configuración de **Nginx**.
- Configurar `logrotate` para **gunicorn** y **nginx**.
- Crear los subdirectorios para Nginx y Gunicorn en `sockets/`, `logs/`, `config/` y `bins/`
- Estructura de archivos (Relativo a `/home/devartis/webapp/`)
  - `config/nginx/default.conf`: Archivo de configuracion *http* o *https*, que tiene un link a `/etc/nginx/site-available/default.conf`
  - `config/gunicorn/config.py`: Configuración  de Gunicorn.
  - `bin/gunicorn/run_gunicorn.sh`: Script para correr Gunicorn.
  - `sockets/gunicorn/gunicorn.sock`: Socket de Unicorn

## Elasticsearch

- Instalar `elasticsearch`
- Configurarlo para que acepte conecciones sólo desde la red privada


## Resultado final

This might be the final file structure:
```
/home/devartis/webapp/
|-- app/ {...}
|-- bin
|   |-- app|   |-- gunicorn
|   |   `-- run_gunicorn.sh
|   |-- nginx
|   `-- postgres
|-- config
|   |-- app
|   |   |-- env
|   |   `-- secret_key
|   |-- gunicorn
|   |   `-- config.py
|   |-- nginx
|   |   `-- default.conf
|   `-- postgres
|-- logs
|   |-- app
|   |-- gunicorn
|   |   |-- access.log
|   |   `-- error.log
|   |-- nginx
|   |   |-- access.log
|   |   `-- error.log
|   `-- postgres
|-- media/
|-- sockets
|   |-- app
|   |-- gunicorn
|   |   |-- gunicorn.pid
|   |   `-- gunicorn.sock
|   |-- nginx
|   `-- postgres
`-- static/
```
