#!/usr/bin/env bash

# install kubernetes code generator
# go get -u k8s.io/code-generator/...

set -eu

go get -u k8s.io/code-generator/...

utildir=$( cd "${0%/*}" && pwd )
rootdir=$( cd "$utildir"/.. && pwd )
gen_ver=$( awk '/k8s.io\/code-generator/ { print $2 }' "$rootdir/go.mod" )
GOPATH=$(go env GOPATH)
codegen_pkg=${GOPATH}/pkg/mod/k8s.io/code-generator@${gen_ver}

ROOT_PACKAGE="github.com/UWNetworksLab/app-defined-networks"

crds=(adncontroller:v1alpha1)

chmod +x "${codegen_pkg}/generate-groups.sh"

bash "${codegen_pkg}/generate-groups.sh" "deepcopy,client,informer,lister" \
  "github.com/UWNetworksLab/app-defined-networks/controller/gen/generated" \
  "github.com/UWNetworksLab/app-defined-networks/controller/gen/apis" \
  "adncontroller:v1alpha1" \
  --go-header-file "${utildir}/boilerplate.go.txt"

cp -R "${GOPATH}/src/${ROOT_PACKAGE}/controller/gen" 'controller/'