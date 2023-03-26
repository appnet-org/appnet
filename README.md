# Application Defined Networks

# Overview

Control plane for Application Defined Networks (ADN). 

Details are avaliable in our whitepaper: [Application Defined Networks](https://xzhu27.me/papers/Application_Defined_Networks_UW_FOCI.pdf)

# Install the CLI

`adnctl` is a command line program to manage ADN control plane. It allows you to interact with your ADN deployment.

## Requirements
- Kubernetes 
  - Run `. ./utils/k8s_setup.sh` to install Kubernetes. (Note - this script is only tested on Ubuntu.)

To install the CLI, run
```bash
. ./install.sh
```

Once installed, verity the CLI is running correctly with:
```bash
adnctl version
```

# Install Controller onto your cluster
Now it's time to install the controller on your cluster.

**TODO**

# Repo Structure
```
Repo Root
|---- cli   
|---- controller   
|---- util
|---- examples
```

# Contact
If you have any questions or comments, please get in touch with Xiangfeng Zhu (xfzhu@cs.washington.edu).