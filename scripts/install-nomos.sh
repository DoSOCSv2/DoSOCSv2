#!/bin/bash
REPO=$(mktemp -d)
echo "[$0] git clone https://github.com/fossology/fossology $REPO"
git clone https://github.com/fossology/fossology $REPO || exit 1
pushd $REPO/src/nomos/agent
yes | mv Makefile.sa Makefile || exit 1
echo "[$0] make"
make || exit 1
echo "[$0] sudo make install"
sudo make install || exit 1
popd
echo "[$0] rm -rvf $REPO"
rm -rvf $REPO
echo "[$0] done!"
