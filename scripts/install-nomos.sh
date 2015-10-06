#!/bin/bash

if [[ "$(type -t git)" == "" ]]; then
    echo "Couldn't find git in your PATH!"
    echo "Please install git before continuing."
    exit 1
fi

if [[ ! -d /usr/include/glib-2.0 ]]; then
    echo "Couldn't find glib-2.0 headers!"
    echo "Please install glib2-devel before continuing."
    exit 1
fi

if [[ "$(type -t gcc)" == "" ]]; then
    echo "Couldn't find gcc in your PATH!"
    echo "Please install gcc before continuing."
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
echo "[$0] rm -rvf $REPO"
rm -rvf $REPO
echo "[$0] sudo ln -s /usr/local/share/fossology/nomos/agent/nomossa /usr/local/bin/nomossa"
sudo ln -s /usr/local/share/fossology/nomos/agent/nomossa /usr/local/bin/nomossa || exit 1
echo "[$0] done!"
