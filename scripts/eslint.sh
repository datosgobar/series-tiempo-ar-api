#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running eslint"
npm run lint
echo "eslint OK :)"

