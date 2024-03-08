# ADN Installation Guide

Welcome to the ADN installation guide. This document provides step-by-step instructions on how to set up ADN and its dependencies.

Requirements:
 - [Kubernetes](#kubernetes) (v1.28+) 
 - [Istio](#installing-adnistio) (v1.20+)
 - [Python](#python) (v3.10+)
 - [Go](#go) (v1.19+)
 - [Rust](#rust) (v1.71+)
 - [protoc](#protoc)


First, clone the ADN repo:
```bash
git clone git@github.com:UWNetworksLab/adn-controller.git
cd adn-controller
```

### Install the CLI

`adnctl` is a command line program to manage the ADN control plane.

To install the CLI, run
```bash
. ./install.sh
```

Once installed, verify the CLI is running correctly with:
```bash
adnctl version
```

Lastly, install the CRDs into the cluster:

```sh
make install
```


## Requirements

### Kubernetes
To install a Kubernetes cluster, we recommend using kubeadm. Follow the steps below:

1. Install the Control Plane:
```bash
. ./util/k8s_setup.sh
```

2. (Optional) Set Up Worker Nodes:
 - First, prepare the worker nodes:
 ```bash
 . ./util/k8s_setup_worker.sh
 ```

 - Then, join the cluster using kubeadm join. Run the following command on the control plane node to get the join command:
 ```bash
 kubeadm token create --print-join-command
 ```

3. Verify Installation:
```bash
kubectl version
```

For additional installation methods (e.g., KIND, Minikube), visit this [page](https://kubernetes.io/docs/tasks/tools/)

We highly recommend installing [k9s](https://k9scli.io/topics/install/) for visualizing your clutser

### Istio

Istio can be installed in either sidecar mode or ambient mode. Choose the one that best fits your requirements:

- Sidecar Mode
```bash
. ./util/istio_setup_sidecar.sh
```

- Ambient Mode
```bash
. ./util/istio_setup_ambient.sh
```


### Python

To install Python, refer to the official [Python Downloads Page]((https://www.python.org/downloads/)).


For Ubuntu users, Python 3.10 can be installed conveniently using the following command:
```bash
. ./util/python310.sh
```

### Go

See this [page](https://go.dev/doc/install) for installation instructions.

### Rust
Install Rust by running the following command:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Protoc
Install the Protocol Buffers Compiler and the necessary Go plugins with these commands:
```bash
sudo apt -y install protobuf-compiler
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```