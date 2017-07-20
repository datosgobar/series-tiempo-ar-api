#!/bin/bash

set -e
DIR=$(dirname "$0")
cd ${DIR}/..


echo "Running jscpd"
jscpd --verbose --o /dev/null --limit 1
echo "jscpd OK :)"

