#!/usr/bin/env bash

set -eu

utildir=$( cd "${0%/*}" && pwd )
rootdir=$( cd "$utildir"/.. && pwd )
gen_ver=$( awk '/k8s.io\/code-generator/ { print $2 }' "$rootdir/go.mod" )
GOPATH=$(go env GOPATH)
codegen_pkg=${GOPATH}/pkg/mod/k8s.io/code-generator@${gen_ver}

chmod +x "${codegen_pkg}/generate-groups.sh"

"${codegen_pkg}/generate-groups.sh" "deepcopy,client,informer,lister" \
  "github.com/UWNetworksLab/app-defined-networks/controller/gen/generated" \
  "github.com/UWNetworksLab/app-defined-networks/controller/gen/apis" \
  adncontroller:v1alpha \
  --go-header-file $utildir/boilerplate.go.txt