#!/bin/bash

set -ex

curl -k -L https://istio.io/downloadIstio | ISTIO_VERSION=1.22.3 sh -
pushd istio-*
sudo cp bin/istioctl /usr/local/bin
istioctl x precheck
istioctl install --set profile=default -y
popd

# turn on auto-injection
# kubectl label namespace default istio-injection=enabled --overwrite

set +ex