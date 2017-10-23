# Features

Currently implemented features

## 503 maintenance page

Every time a build is run (update or deploy) the application will be disabled and a 503 page will be shown.
This is covered by the `maintenance` role.

## Logrotate

Nginx and Gunicorn logs are rotated by configuration files.
This is covered by `web_server` role, in the file `tasks/configure_logrotate.yml`

## Django Secret Key

This is generated once when the application if deployed. The result is saved at `config/app/secret_key`.
If it gets deleted, it will be regenerated, but never the same value.

This is covered by the `django_application` role, and the generator script is located at `files/django_secret_key.py`.

## Firewall

A firewall is installed and only allows incoming connection for ports:

- 22
- 80
- 443

## Nginx http and https (WIP)

By default a server at port `80` will be up. If you want to set up a https server, must follow these instructions:

The `web_server` role will look at `config/nginx/` for `site.crt`, `site.key` and `site.domain` files.
If they exist, must contain the following values:

- `site.crt`: ssl certificate
- `site.key`: ssl secret key
- `site.domain`: Application domain (e.g. `mydomain.com`)

**Note:** site.domain file must be a _one-line_ file and should not include a `www.` part, it will be included automatically.

After add that files, run a full deployment. It will re-write the nginx settings using HTTPS.

## Nginx http auth

Http auth can be enable by adding the auth file at `/home/devartis/webapp/conf/nginx/`, and then run a full deployment.
It will re-write the nginx settings.
For generating the auth file, the following command could be used (Replace $AUTH_USER with your preferred http auth user):

    htpasswd -c /home/devartis/conf/nginx/.htpasswd $AUTH_USER

## Database backups

A database backups is made every week and before running the migrations.
The backups are stored at `/home/devartis/webapp/backups/postgresql/`.
The backup script is located at `/home/devartis/webapp/bins/postgresql/psql_backup.sh`