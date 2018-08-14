# Development
A continuación se detallan los pasos a seguir para levantar una versión local de la aplicación, apuntado a futuros desarrolladores de la misma. Este documento asume un entorno Linux para el desarrollo, y fue probado bajo Ubuntu 16.04.

## Requerimientos

- Python 2.7.6
- Virtualenv
- Docker
- Docker compose

## Setup

### Virtualenv (con Pyenv)
Es recomendable instalar las dependencias de la aplicación en un _entorno virtual_ para evitar conflictos con otras aplicaciones de versionado de las librerías usadas. Este ejemplo instala un entorno virtual de Python 2.7.6 con el nombre `stiempo-api`, y todas las dependencias de la aplicación.
```bash
pyenv virtualenv 2.7.6 stiempo-api
pyenv activate stiempo-api
pip install -r requirements/local.txt
```

### Configuración
Algunas configuraciones locales (como variables de entorno, o la base de datos usada) pueden llegar a diferir de la versión productiva, y deben ser seteadas manualmente. Para ello se provee una configuración de _ejemplo_, que puede ser usada como base. 
```bash
cp conf/settings/local_example.py conf/settings/local.py
cp conf/settings/.env.default_local conf/settings/.env
```

A su vez, se debe informar a Django cual es el módulo de configuración a leer. Este módulo debe ser el mismo que fue copiado en el paso anterior (`conf/settings/local.py` en el ejemplo). Esto se hace seteando la variable de entorno `DJANGO_SETTINGS_MODULE`, lo cual se puede hacer persistente entre sesiones de terminal escribiéndolo en `.bashrc` (o similar, dependiendo de la terminal utilizada):
```bash
export DJANGO_SETTINGS_MODULE=conf.settings.local
```

### Servicios
Los servicios (PostgreSQL, Elasticsearch, Redis) pueden ser levantados usando Docker y Docker Compose:
```bash
docker-compose pull
docker-compose up -d
```

### Base de datos
Correr las migraciones de las base de datos:
```bash
python manage.py migrate
```

### Worker
Levanta los workers para ejecutar tareas asincrónicas. Notar que esta tarea bloquea la terminal.

```bash
python manage.py rqworker high default low scrapping
```

### Web server
Este comando levanta la aplicación. 
```bash
python manage.py runserver
```

Si está todo en orden se podrá leer algún mensaje como el siguiente:
```bash
Django version 1.11.6, using settings 'conf.settings.local'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Tests
Correr `scripts/tests.sh` desde el directorio raíz. También se proveen scripts que chequean estilos (`scripts/pycodestyle.sh`) y `pýlint` (`scripts/pylint.sh`)
