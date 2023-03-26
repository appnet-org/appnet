#!/bin/bash
set -e

echo $ADN_DIR 
if [ -z "${ADN_DIR}" ]; then
    echo "not set"
else
    echo "set"
fi
