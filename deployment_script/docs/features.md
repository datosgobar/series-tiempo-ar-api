# Features

## 503 maintenance page

Con cada deployment (actualización o deployment completo), la aplicación mostrará una página de 503.
Ver el Role "maintenance" para mas detalles.

## Logrotate

Los logs de Nginx & Gunicorn logs son rotados periodicamente..
En el Role `web_server`, el archivo `tasks/configure_logrotate.yml` define cómo se implementa.

## Django Secret Key

Esta Key de Django es generada sólo una vez, en el primer deployment.
El resultado es guardado en `config/app/secret_key`.
Si ese archivo es borrado, una nueva clave será utilizada.

En el Role `django_application`, hay un script que genera esta Key `files/django_secret_key.py`.

## Firewall

`UFW` es instalado y sólo permite conecciones a los siguientes puertos para el servidor web:

- 22
- 80
- 443

Para elasticsearch, el único puerto es el `22` desde cualquier IP y el rango de 9200-9400 desde IP en la red privada.


## Nginx - http & https

Por defecto el servidor utilizará el puerto 80.
Para utilizar `https`, se debe seguir las siguientes instrucciones:

En el directorio `config/nginx/` agregar los siguientes archivos:

- `site.crt`: Certificado ssl
- `site.key`: Clave secreta SSH (ssl secret key)
- `site.domain`: Dominio de la aplicación (e.g. `mydomain.com`)

**Importante:** El archivo `site.domain` debe contentes _solo una línea_ y no incluir `www.`.

Después de agregar esos archivos, correr un deployment completo, esto reescribirá la configuracion de Nginx

## Nginx - http auth


"Http auth" Puede ser activado mediante agregar un archivo en `/home/devartis/webapp/conf/nginx/`, y luego correr un deployment completo.

Para generar este archivo, el siguiente comando podría ser usado (Reemplazar $AUTH_USER con uno a elección):

    htpasswd -c /home/devartis/conf/nginx/.htpasswd $AUTH_USER

## Backups

El backup de la base de datos es hecho cada semana y antes de correr migraciones.
Los backups son guardados en `/home/devartis/webapp/backups/postgresql/`.
El script para correrlo manualmente se encuentra en `/home/devartis/webapp/bins/postgresql/psql_backup.sh`
