#!/bin/bash

valid_cni=("cilium" "flannel")
cni="flannel"

while getopts ":hc:" opt; do
  case $opt in
    h)
      echo "Usage: $0 [-c cni]"
      echo "  -c   Proxy to use (valid options are: ${valid_cni[*]})"
      exit 0
      ;;
    c)
      cni="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [[ " ${valid_cni[*]} " =~ " ${cni} " ]]; then
    echo "Option '$cni' is valid"
else
    echo "Invalid option: $cni"
    echo "Valid options are: ${valid_cni[*]}"
    exit 1
fi

set -ex

sudo modprobe br_netfilter
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sudo sysctl --system


sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y


curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null


sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io -y

sudo mkdir -p /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

sudo systemctl enable docker
sudo systemctl daemon-reload
sudo systemctl restart docker


sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

sudo mkdir -p /etc/apt/keyrings
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

sudo apt-get update -y

# sudo apt-get install -y kubelet kubeadm kubectl
# sudo apt-get install -y kubelet=1.24.4-00 kubeadm=1.24.4-00 kubectl=1.24.4-00
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

sudo swapoff -a


sudo rm -f "/etc/containerd/config.toml"

sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo systemctl restart containerd

# This is important since kubeadm reset does not clear that.
sudo rm -f /etc/cni/net.d/*

# run cilium uninstall if cilium is installed.
if type cilium >/dev/null 2>&1; then
  cilium uninstall >/dev/null 2>&1
fi

sudo kubeadm reset -f
sudo rm -rf $HOME/.kube

### for data plane (kubeadm token create --print-join-command)
# kubeadm join xxx

echo "alias k='kubectl'" >> ~/.bashrc
. ~/.bashrc

sudo apt-get update
sudo apt-get install -y linux-tools-common linux-tools-generic linux-tools-`uname -r`
sudo apt-get install -y sysstat

# Create a directory for AppNet plugins
mkdir -p /tmp/appnet

set +ex
