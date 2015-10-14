#!/bin/bash

DC_PATH=/usr/local/dependency-check/bin/dependency-check.sh

if [[ -x $DC_PATH ]]; then
    echo "[$0] Looks like dependency-check is already installed at $DC_PATH"
    echo "[$0] Doing nothing."
    exit 0
fi

TEMPDIR=$(mktemp -d)
pushd $TEMPDIR
mkdir dependency-check
cd dependency-check
wget http://dl.bintray.com/jeremy-long/owasp/dependency-check-1.2.11-release.zip || exit 1
unzip dependency-check-1.2.11-release.zip || exit 1
rm dependency-check-1.2.11-release.zip
cd ..
echo "[$0] sudo mv dependency-check /usr/local"
sudo mv dependency-check /usr/local || exit 1
sudo mkdir /var/lib/dependency-check || exit 1
sudo ln -sf /var/lib/dependency-check /usr/local/dependency-check/data || exit 1
sudo chmod +x $DC_PATH || exit 1
mkdir empty
sudo $DC_PATH --app null --scan empty
popd
sudo rm -rf "$TEMPDIR"
