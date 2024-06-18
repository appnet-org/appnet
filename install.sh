#!/bin/bash

# Install Go if not found
if ! command -v go &> /dev/null
then
    echo "Go not found. Installing Go"
    wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.22.2.linux-amd64.tar.gz

    echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
    source ~/.bashrc
    rm go1.22.2.linux-amd64.tar.gz
fi

set -e

if [ -z "${APPNET_DIR}" ]; then
  echo "Setting APPNET_DIR to current directory"
  echo "export APPNET_DIR=$PWD" >> ~/.bashrc
  . ~/.bashrc
fi


GO_PATH=$(go env GOPATH)
GO_BIN_DIR=$(go env GOPATH)/bin
echo "export PATH=$PATH:$GO_BIN_DIR" >> ~/.bashrc
echo "export GOPATH=$GO_PATH" >> ~/.bashrc
. ~/.bashrc

echo "Building appnetctl..."
cd $APPNET_DIR/appnetctl
go install

cd $APPNET_DIR

echo "appnetctl was successfully installed 🎉🎉🎉"
echo ""

echo "Installing Rust Dependencies"
cargo install cargo-wasi
rustup target add wasm32-wasi

# Python dependencies
pip install lark pre-commit tomli tomli_w colorlog rich kubernetes pyyaml


go install golang.org/x/tools/cmd/goimports@latest
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

set +e
