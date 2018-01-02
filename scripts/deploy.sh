#!/bin/bash

echo "Copiando key..."
echo $DEPLOY_TARGET_PUBKEY > "/tmp/$DEPLOY_TARGET_USERNAME.key"

echo "Ingresando al servidor remoto..."
ssh -vvv $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT -i "/tmp/$DEPLOY_TARGET_USERNAME.key" "ls -lsa"

echo "Eliminando key..."
rm "/tmp/$DEPLOY_TARGET_USERNAME.key"
