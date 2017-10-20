#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..


echo "Running pep8"
pep8 series_tiempo_ar_api --max-line-length=140 --ignore=E731 --exclude=**/migrations/,__init__.py

echo "pep8 OK :)"
