#!/usr/bin/env bash

WORKDIR=`dirname $(realpath $0)`
cd $WORKDIR

tinygo build -o helloworld_go.wasm -scheduler=none -target=wasi ./main.go
cp helloworld_go.wasm /tmp

