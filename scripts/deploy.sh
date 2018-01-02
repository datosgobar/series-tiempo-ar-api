#!/bin/bash

echo "Ingresando al servidor remoto..."
ssh -vvv $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT "cd ~/series-tiempo-ar-deploy && ansible-playbook -i inventories/testing/hosts --vault-password-file vault_pass.txt site.yml -vvv"
