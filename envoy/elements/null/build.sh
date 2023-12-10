#!/usr/bin/env bash

WORKDIR=`dirname $(realpath $0)`
cd $WORKDIR

cargo build --target=wasm32-unknown-unknown --release
# TODO: Change null to your wasm filter name
cp target/wasm32-unknown-unknown/release/null.wasm /tmp

