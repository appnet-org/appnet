
#!/bin/bash

set -ex

curl -k -L https://istio.io/downloadIstio | ISTIO_VERSION=1.22.3 sh -
pushd istio-*
sudo cp bin/istioctl /usr/local/bin
kubectl get crd gateways.gateway.networking.k8s.io &> /dev/null || \
  { kubectl kustomize "github.com/kubernetes-sigs/gateway-api/config/crd/experimental?ref=v1.0.0" | kubectl apply -f -; }
istioctl install --set profile=ambient --set "components.ingressGateways[0].enabled=true" --set "components.ingressGateways[0].name=istio-ingressgateway" --skip-confirmation --set hub=docker.io/appnetorg --set "values.global.imagePullPolicy=Always"
popd

set +ex