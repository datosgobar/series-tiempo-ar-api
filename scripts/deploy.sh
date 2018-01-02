#!/bin/bash

echo "Ingresando al servidor remoto..."
ssh -vvv $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT "ls -lsa"
