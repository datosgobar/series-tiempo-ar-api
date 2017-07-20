#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
pylint -f parseable elastic_spike --rcfile=.pylintrc
echo "pylint OK :)"
