#!/bin/bash

set -e;

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ENVIRONMENT="$1"

# Cargo variables dependiendo del ambiente
. "$DIR/variables.sh" "$ENVIRONMENT"
"$DIR/prepare.sh"
"$DIR/deploy.sh" "$ENVIRONMENT"
