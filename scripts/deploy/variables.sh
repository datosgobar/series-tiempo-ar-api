#!/usr/bin/env bash

ENVIRONMENT="$1"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# NOTA: para agregar un nuevo ambiente, se necesitan todas estas variables,
# pero usando otros prefijos (en testing es TESTING_* )

if [ "$ENVIRONMENT" == "testing" ]; then
    export vault_key_var_name="encrypted_f201276fd578_key"
    export vault_iv_var_name="encrypted_f201276fd578_iv"

    export ssh_key_var_name="encrypted_ae74091d1bce_key"
    export ssh_iv_var_name="encrypted_ae74091d1bce_iv"

    export DEPLOY_TARGET_SSH_PORT="$TESTING_DEPLOY_TARGET_SSH_PORT"
    export DEPLOY_TARGET_USERNAME="$TESTING_DEPLOY_TARGET_USERNAME"
    export DEPLOY_TARGET_IP="$TESTING_DEPLOY_TARGET_IP"
    export DEPLOY_ENVIRONMENT="$ENVIRONMENT"
else
    echo "Ambiente '$ENVIRONMENT' desconocido";
    exit 1;
fi
