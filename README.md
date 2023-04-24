# Application Defined Networks

# Overview

Control plane for Application Defined Networks (ADN). 

Details are avaliable in our whitepaper: [Application Defined Networks](https://xzhu27.me/papers/Application_Defined_Networks_UW_FOCI.pdf)

## Requirements
- Kubernetes and Docker
  - Run `. ./utils/k8s_setup.sh` to install Kubernetes via kubeadm. (Note - this script is only tested on Ubuntu 20.04.)
  - You can use [KIND](https://sigs.k8s.io/kind) to get a local cluster for testing
- Go (Ideally 1.19+)

### Install the CLI

`adnctl` is a command line program to manage ADN control plane. 

To install the CLI, run
```bash
. ./install.sh
```

Once installed, verity the CLI is running correctly with:
```bash
adnctl version
```

### Running on the cluster
1. Install Instances of Custom Resources:

```sh
kubectl apply -f config/samples/
```

2. Build and push your image to the location specified by `IMG`:

```sh
make docker-build docker-push IMG=xzhu0027/app-defined-networks:latest
```

3. Deploy the controller to the cluster with the image specified by `IMG`:

```sh
make deploy IMG=xzhu0027/app-defined-networks:latest
```

### Uninstall CRDs
To delete the CRDs from the cluster:

```sh
make uninstall
```

### Undeploy controller
UnDeploy the controller from the cluster:

```sh
make undeploy
```

### How it works
This project aims to follow the Kubernetes [Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/).

It uses [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/),
which provide a reconcile function responsible for synchronizing resources until the desired state is reached on the cluster.

### Test It Out
1. Install the CRDs into the cluster:

```sh
make install
```

2. Run your controller (this will run in the foreground, so switch to a new terminal if you want to leave it running):

```sh
make run
```

**NOTE:** You can also run this in one step by running: `make install run`

### Modifying the API definitions
If you are editing the API definitions, generate the manifests such as CRs or CRDs using:

```sh
make manifests
```

**NOTE:** Run `make --help` for more information on all potential `make` targets

# Contact

If you have any questions or comments, please get in touch with Xiangfeng Zhu (xfzhu@cs.washington.edu).
