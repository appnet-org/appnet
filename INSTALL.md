# Installing ADN


Requirements:
 - [Kubernetes](#kubernetes) (v1.28+) 
 - [Istio](#installing-adnistio) (v1.20+)
 - [Python](#python) (v3.10+)
 - [Go](#go) (v1.19+)
 - [Rust](#rust) 
 - [protoc](#protoc)


## Kubernetes
There are multiple options to install a Kubernetes cluster, we recommend using kubeadm.
```bash
# Install the control plane
. ./util/k8s_setup.sh

# Optionally, to set up the worker nodes, first run 
. ./util/k8s_setup_worker.sh

# Then join the cluster via kubeadm join
kubeadm join xxx # Run kubeadm token create --print-join-command on the control plane node.

# Finally, verify the installation
kubectl version
```

See this [page](https://kubernetes.io/docs/tasks/tools/) for other install tools (e.g., KIND or minikuube).


## Istio

There are two options to install istio: the sidecar mode and the ambient mode:

```bash
# Sidecar mode
. ./util/istio_setup_sidecar.sh

# Ambient mode
. ./util/istio_setup_ambient.sh
```

## Python

See this [page](https://www.python.org/downloads/) for installation instructions.

For convenience to install Python 3.10 on Ubuntu, run:
```bash
. ./util/python310.sh
```

## Go

See this [page](https://go.dev/doc/install) for installation instructions.

## Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Protoc

```bash
sudo apt -y install protobuf-compiler
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```