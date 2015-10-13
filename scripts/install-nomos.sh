#!/bin/bash

NOMOSSA_PATH=/usr/local/bin/nomossa
if [[ -f $NOMOSSA_PATH ]]; then
    echo "[$0] Looks like nomos is already installed at $NOMOSSA_PATH"
    echo "[$0] Doing nothing."
    exit 0
fi

if [[ "$(type -t git)" == "" ]]; then
    echo "[$0] Couldn't find git in your PATH!"
    echo "[$0] Please install git before continuing."
    exit 1
fi

if [[ ! -d /usr/include/glib-2.0 ]]; then
    echo "[$0] Couldn't find glib-2.0 headers!"
    echo "[$0] Please install glib2-devel before continuing."
    exit 1
fi

if [[ "$(type -t gcc)" == "" ]]; then
    echo "[$0] Couldn't find gcc in your PATH!"
    echo "[$0] Please install gcc before continuing."
    exit 1
fi

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
echo "[$0] rm -rf $REPO"
rm -rf $REPO
echo "[$0] sudo ln -s /usr/local/share/fossology/nomos/agent/nomossa $NOMOSSA_PATH"
sudo ln -s /usr/local/share/fossology/nomos/agent/nomossa $NOMOSSA_PATH || exit 1
echo "[$0] done!"
