#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
pylint -f parseable series_tiempo_ar_api --rcfile=.pylintrc
echo "pylint OK :)"
