#!/usr/bin/env bash

WORKDIR=`dirname $(realpath $0)`
cd $WORKDIR

cargo build --target=wasm32-unknown-unknown --release
cp target/wasm32-unknown-unknown/release/acl.wasm /tmp

