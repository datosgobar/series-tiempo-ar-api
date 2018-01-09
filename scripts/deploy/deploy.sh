#!/bin/bash

set -e;
# Nota: Las variables no definidas aqui deben ser seteadas en ./variables.sh

# TODO: Mejorar esta script.
echo "Ejecutando comando de instalación..."
ssh $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT "\
    cd ~/series-tiempo-ar-deploy &&\
    git pull &&\
    source ./env/bin/activate &&\
    ansible-playbook -i inventories/$DEPLOY_ENVIRONMENT/hosts --extra-vars='checkout_branch=$DEPLOY_REVISION' --vault-password-file vault_pass.txt site.yml -vvv &&\
    rm -f vault_pass.txt"
