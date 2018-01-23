#!/usr/bin/env bash

set -e;

# Nota: Las variables no definidas aqui deben ser seteadas en ./variables.sh
# si tenes dudas sobre la sintaxis ${!variable}, mira https://stackoverflow.com/a/1921337/2355756


deployment_files="scripts/deploy/files/$DEPLOY_ENVIRONMENT"

echo "Inicializando known_hosts"
# Agrego el host a known_hosts
ssh-keyscan -p $DEPLOY_TARGET_SSH_PORT -t 'rsa,dsa,ecdsa' -H $DEPLOY_TARGET_IP 2>&1 | tee -a $HOME/.ssh/known_hosts

echo "Inicializando acceso ssh"
# Desencripto la key ssh para acceder al server
openssl aes-256-cbc -K ${!ssh_key_var_name} -iv ${!ssh_iv_var_name} -in $deployment_files/build\+ts-api@travis-ci.org.enc -out /tmp/build\+ts-api@travis-ci.org -d
chmod 600 /tmp/build\+ts-api@travis-ci.org

