#!/bin/bash

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
