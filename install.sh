#!/bin/bash

SELF=$(basename $0)

if [[ ! -x ./install.sh ]]; then
    echo $SELF: must run from own directory
    exit 1
fi

printf "$SELF: Checking for Python 2.7.x..."
PY2_VERSION=$(python2 --version 2>&1)
if [[ $PY2_VERSION < 'Python 2.7.0' ]]; then
    printf "python2 executable not found or not recent enough. "
    printf "Please install Python 2.7.x.\n"
    exit 1
fi
printf "ok.\n"

printf "$SELF: Checking for pip2..."
which pip2 > /dev/null
if [[ "$?" != "0" ]]; then
    printf "not found. Please install your distribution's version of pip "
    printf "(typically packaged as 'python-pip' or "
    printf "'python2-pip')\n"
    exit 1
fi
printf "ok.\n"

printf "$SELF: Checking for cp2foss..."
which cp2foss > /dev/null
if [[ "$?" != "0" ]]; then
    printf "not found. Please install FOSSology >= 2.6 "
    printf "from http://www.fossology.org\n"
    exit 1
fi
printf "ok.\n"

printf "$SELF: Installing packages from requirements.txt...\n"
pip2 install -r ./requirements.txt
if [[ "$?" != "0" ]]; then
    printf "$SELF: pip returned nonzero exit status. Giving up.\n"
    exit 1
fi
printf "$SELF: ok.\n"
printf "\n"
printf "$SELF: All done! Be sure to edit your settings.py to set your scanner "
printf "path and database connection URI.\n"
