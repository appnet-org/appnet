#!/usr/bin/env bash

set -eu

utildir=$( cd "${0%/*}" && pwd )
rootdir=$( cd "$utildir"/.. && pwd )
gen_ver=$( awk '/k8s.io\/code-generator/ { print $2 }' "$rootdir/go.mod" )
GOPATH=$(go env GOPATH)
codegen_pkg=${GOPATH}/pkg/mod/k8s.io/code-generator@${gen_ver}


ROOT_PACKAGE="https://"github.com/UWNetworksLab/app-defined-networks"

crds=(adnconfig:v1alpha)

chmod +x "${codegen_pkg}/generate-groups.sh"

GO111MODULE='on' "${codegen_pkg}/generate-groups.sh" \
  'deepcopy,client,informer,lister' \
  "${ROOT_PACKAGE}/controller/pkg/client" \
  "${ROOT_PACKAGE}/controller/pkg/apis" \
  "${crds[*]}" \
  --go-header-file "${codegen_pkg}"/hack/boilerplate.go.txt