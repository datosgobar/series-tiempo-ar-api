# Series de tiempo AR - Deployment

- This repository must allow any (privileged) user to deploy the application.
- It must be simple and predictible.
- It is tested against Ubuntu 16.04.

## Idea

See [Idea](docs/idea.md)

## Features

See [Features](docs/features.md)

## Requirements

- Ansible: `pip install -r requirements.txt`
- SSH client
  - Ubuntu: `apt-get install openssh-client`
  - Arch linux: `pacman -S openssh` ([docs](https://wiki.archlinux.org/index.php/Secure_Shell#OpenSSH))

### Deploy

For deploying, some extra vars must be passsed:

    export POSTGRESQL_USER=database_user  # Set psql user name
    export POSTGRESQL_PASSWORD=database_password_xxxxxxx  # Set psql user password
    export INVENTORY=inventories/staging/hosts
    export LOGIN_USER=root  # The user with sudo access.

    bash deploy.sh -p $POSTGRESQL_USER -P $POSTGRESQL_PASSWORD \
        -i $HOST -l $LOGIN_USER

### Update

For updating, use the update.sh script:

    bash update.sh -i $HOST -l $LOGIN_USER

## Separar Elas
