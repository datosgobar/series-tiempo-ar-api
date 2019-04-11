#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
if [[ "$1" = "--full" ]]; then
    pylint -f parseable series_tiempo_ar_api --rcfile=.pylintrc
else
    git diff --name-only origin/master |
    grep '^series_tiempo_ar_api/.*\.py$' |
    grep -v migrations |
    grep -v settings |
    xargs -r pylint --rcfile=.pylintrc -f parseable
fi
echo "pylint OK :)"
