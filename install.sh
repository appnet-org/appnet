#!/bin/bash

set -eu

install_go=false

while getopts "g" opt; do
  case ${opt} in
    g)
      install_go=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

if [ -z "${ADN_DIR}" ]; then
  echo "Setting ADN_DIR to current directory"
  echo "export ADN_DIR=$PWD" >> ~/.bashrc
  . ~/.bashrc
fi


if [ "${install_go}" = true ]; then
    echo "Installing Go"
    wget https://go.dev/dl/go1.20.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.20.linux-amd64.tar.gz

    echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
    . ~/.bashrc

    GO_PATH=$(go env GOPATH)
    GO_BIN_DIR=$(go env GOPATH)/bin
    echo "export PATH=$PATH:$go_bin_dir" >> ~/.bashrc
    echo "export GOPATH=$PATH:$go_bin_dir" >> ~/.bashrc
    . ~/.bashrc
fi

echo "Building adnctl..."
cd $ADN_DIR/cli
go install 
mv $go_bin_dir/cli $go_bin_dir/adnctl


echo "adnctl was successfully installed 🎉🎉🎉"
echo ""