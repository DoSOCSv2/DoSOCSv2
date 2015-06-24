#!/bin/bash

SELF=$(basename $0)

printf "$SELF: Checking for Python 2.7.x..."
PY2_VERSION=$(/usr/bin/env python2 --version 2>&1 | cut -c 8- )
if [[ $PY2_VERSION < '2.7.0' ]]; then
    printf "python2 executable not found or not recent enough. "
    printf "Please install Python 2.7.x.\n"
    exit 1
fi
printf "ok.\n"

printf "$SELF: Checking for cp2foss..."
which cp2foss > /dev/null
if [[ "$?" != "0" ]]; then
    printf "not found. Please install FOSSology >= 2.5 "
    printf "from http://www.fossology.org\n"
    exit 1
fi
printf "ok.\n"
