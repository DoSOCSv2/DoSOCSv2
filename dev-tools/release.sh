#!/bin/bash

if [[ "$1" == "minor" ]]; then
    BUMPER='./dev-tools/minor-bump.py'
elif [[ "$1" == "fix" ]]; then
    BUMPER='./dev-tools/fix-bump.py'
else
    echo "usage: $0 (minor | fix)"
    exit 1
fi

OLDVER=$(cat setup.py | grep -E '^_dosocs2_version = ' | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+')
NEWVER=$($BUMPER $OLDVER)

sed -i "s/$OLDVER/$NEWVER/g" setup.py
sed -i "s/$OLDVER/$NEWVER/g" dosocs2/dosocs2.py

git commit -m "Bump version number to $NEWVER" -e
