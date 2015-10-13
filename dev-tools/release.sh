#!/bin/bash

if [[ "$1" == "minor" ]]; then
    BUMPER='./dev-tools/minor-bump.py'
elif [[ "$1" == "fix" ]]; then
    BUMPER='./dev-tools/fix-bump.py'
else
    echo "usage: $0 (minor | fix)"
    exit 1
fi

STATUS=$(git status | grep "nothing to commit, working directory clean")

if [[ "$?" != "0" ]]; then
    echo "$0: working directory must be clean first"
    exit 1
fi

if [[ "${VIRTUAL_ENV}x" != "x" ]]; then
    echo "$0: get out of virtual env first"
    exit 1
fi

OLDVER=$(cat setup.py | grep -E '^_dosocs2_version = ' | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+')
NEWVER=$($BUMPER $OLDVER)

sed -i "s/$OLDVER/$NEWVER/g" setup.py
git add setup.py
sed -i "s/$OLDVER/$NEWVER/g" dosocs2/dosocs2.py
git add dosocs2/dosocs2.py

git commit -m "Bump version number to $NEWVER" -e

if [[ "$?" != "0" ]]; then
    git reset HEAD .
    git checkout -- .
    exit 1
fi

python setup.py sdist || exit 1
