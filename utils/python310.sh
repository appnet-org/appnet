#!/bin/bash

set -e

# Install python3.10
echo "Installing Python3.10"
sudo apt update
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev wget libbz2-dev
wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
tar -xf Python-3.10.0.tgz
cd Python-3.10.0
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
pip3.10 install lark pre-commit tomli tomli_w colorlog rich kubernetes pyyaml

echo "Installing Rust"
curl https://sh.rustup.rs -sSf | sh -s -- -y

set +e
