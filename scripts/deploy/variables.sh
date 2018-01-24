#!/usr/bin/env bash

ENVIRONMENT="$1"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# NOTA: para agregar un nuevo ambiente, se necesitan todas estas variables,
# pero usando otros prefijos (en testing es TESTING_* )

if [ "$ENVIRONMENT" == "testing" ]; then
    echo "Ambiente $ENVIRONMENT"
    # Las siguientes variables definen cuales variables buscar para desencriptar
    # algunos valores de travis. Ver ./prepare.sh para mas info
    export ssh_key_var_name="encrypted_27b45b79a046_key"
    export ssh_iv_var_name="encrypted_27b45b79a046_iv"

    # Las siguientes variables son de conexion ssh
    export DEPLOY_TARGET_VAULT_PASS_FILE="$TESTING_DEPLOY_VAULT_PASS_FILE"
    export DEPLOY_TARGET_SSH_PORT="$TESTING_DEPLOY_TARGET_SSH_PORT"
    export DEPLOY_TARGET_USERNAME="$TESTING_DEPLOY_TARGET_USERNAME"
    export DEPLOY_TARGET_IP="$TESTING_DEPLOY_TARGET_IP"
    export DEPLOY_ENVIRONMENT="$ENVIRONMENT"
    export DEPLOY_REVISION="master"
elif [ "$ENVIRONMENT" == "staging" ]; then
    echo "Ambiente $ENVIRONMENT"
    export ssh_key_var_name="encrypted_4551c5846e4a_key"
    export ssh_iv_var_name="encrypted_4551c5846e4a_iv"

    # Las siguientes variables son de conexion ssh
    export DEPLOY_TARGET_VAULT_PASS_FILE="$STAGING_DEPLOY_VAULT_PASS_FILE"
    export DEPLOY_TARGET_SSH_PORT="$STAGING_DEPLOY_TARGET_SSH_PORT"
    export DEPLOY_TARGET_USERNAME="$STAGING_DEPLOY_TARGET_USERNAME"
    export DEPLOY_TARGET_IP="$STAGING_DEPLOY_TARGET_IP"
    export DEPLOY_ENVIRONMENT="$ENVIRONMENT"
    export DEPLOY_REVISION="${TRAVIS_TAG:-$TRAVIS_COMMIT}" # Desde el tag o el hash del commit
else
    echo "Ambiente '$ENVIRONMENT' desconocido";
    exit 1;
fi
