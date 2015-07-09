#!/bin/bash
[[ "$1" == "" ]] && printf 'You must specify a file argument\n' && exit 1

LIBSFILE=$1

# the below regex converts the 'pip list' style to the 'pip freeze'
# style of package spec
cat $LIBSFILE | sed -r 's/ \((.*?)\)/==\1/g' | while read item; do
    pip install -d . --no-binary :all: --no-compile -I $item
done
     
shopt -s nullglob
for item in *.bz2 *.gz *.zip *.tar; do
   PVERSION=$(ls -1 $item | grep -Eo '[0-9]+\.[0-9]+(\.[0-9]+)?')
   PNAME=$(ls -1 $item | sed -r 's/-[0-9]+\.[0-9]+(\.[0-9]+)?.*//g')
   dosocs2 scan --package-version=$PVERSION --package-name=$PNAME $item
done
shopt -u nullglob
