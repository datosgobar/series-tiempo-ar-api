#!/usr/bin/env bash

ENVIRONMENT="$1"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# NOTA: para agregar un nuevo ambiente, se necesitan todas estas variables,
# pero usando otros prefijos (en testing es TESTING_* )

export OVPN_CONFIG="client"
export OVPN_PATH="/etc/openvpn/$OVPN_CONFIG.conf"

# Las siguientes variables definen cuales variables buscar para desencriptar
# algunos valores de travis. Ver ./prepare.sh para mas info


if [ "$ENVIRONMENT" == "testing" ]; then
    echo "Ambiente $ENVIRONMENT"

    export USE_VPN="" # Do not use VPN

    export DEPLOY_TARGET_VAULT_PASS_FILE="$TESTING_DEPLOY_VAULT_PASS_FILE"
    export DEPLOY_TARGET_SSH_PORT="$TESTING_DEPLOY_TARGET_SSH_PORT"
    export DEPLOY_TARGET_USERNAME="$TESTING_DEPLOY_TARGET_USERNAME"
    export DEPLOY_TARGET_IP="$TESTING_DEPLOY_TARGET_IP"
    export DEPLOY_ENVIRONMENT="$ENVIRONMENT"
    export DEPLOY_REVISION="master"
elif [ "$ENVIRONMENT" == "staging" ]; then
    echo "Ambiente $ENVIRONMENT"

    export USE_VPN="$STAGING_USE_VPN"

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
