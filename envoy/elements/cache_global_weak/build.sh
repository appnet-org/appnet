#!/usr/bin/env bash

WORKDIR=`dirname $(realpath $0)`
cd $WORKDIR

cargo build --target=wasm32-wasi --release
cp target/wasm32-wasi/release/cache_global_weak.wasm /tmp

