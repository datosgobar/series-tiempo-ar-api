#!/bin/bash

echo "Ejecutando comando de instalación..."
ssh $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT "cd ~/series-tiempo-ar-deploy && source ./env/bin/activate && ansible-playbook -i inventories/testing/hosts --vault-password-file vault_pass.txt site.yml -vvv"
