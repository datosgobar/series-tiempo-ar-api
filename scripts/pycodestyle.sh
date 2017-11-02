#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..


echo "Running pycodestyle"
pycodestyle series_tiempo_ar_api -v

echo "pep8 OK :)"
