#!/bin/bash

set -ex

# Install wrk and wrk2
sudo apt-get install luarocks -y
sudo luarocks install luasocket

git clone https://github.com/wg/wrk.git
pushd wrk
make -j $(nproc)

popd

sudo apt-get install libssl-dev -y
sudo apt-get install libz-dev -y 

git clone https://github.com/giltene/wrk2.git
pushd wrk2
make -j $(nproc)

popd

set +ex
