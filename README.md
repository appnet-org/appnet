<p align="center">
  <picture>
    <img alt="AppNet" src="https://raw.githubusercontent.com/appnet-org/docs/main/src/assets/logos/AppNet-blue.png" width=35%>
  </picture>
</p>

<h3 align="center">
Expressive, Easy to Build, and High-Performance Application Networks
</h3>

[![Go Report Card](https://goreportcard.com/badge/github.com/appnet-org/appnet)](https://goreportcard.com/report/github.com/appnet-org/appnet)

## To start using AppNet

See our documentation on [appnet.wiki](https://appnet.wiki).

## To learn more about AppNet

See our NSDI [paper](https://www.usenix.org/system/files/nsdi25-zhu.pdf).


## To start developing AppNet

See our developer's guide on [appnet.wiki/developer](https://appnet.wiki/developer.html)

<!-- 
## Description
// TODO(user): An in-depth paragraph about your project and overview of use

## Getting Started

### Prerequisites
- go version v1.21.0+
- docker version 17.03+.
- kubectl version v1.11.3+.
- Access to a Kubernetes v1.11.3+ cluster.

### To Deploy on the cluster
**Build and push your image to the location specified by `IMG`:**

```sh
make docker-build docker-push IMG=<some-registry>/appnet:tag
```

**NOTE:** This image ought to be published in the personal registry you specified. 
And it is required to have access to pull the image from the working environment. 
Make sure you have the proper permission to the registry if the above commands don’t work.

**Install the CRDs into the cluster:**

```sh
make install
```

**Deploy the Manager to the cluster with the image specified by `IMG`:**

```sh
make deploy IMG=<some-registry>/appnet:tag
```

> **NOTE**: If you encounter RBAC errors, you may need to grant yourself cluster-admin 
privileges or be logged in as admin.

**Create instances of your solution**
You can apply the samples (examples) from the config/sample:

```sh
kubectl apply -k config/samples/
```

>**NOTE**: Ensure that the samples has default values to test it out.

### To Uninstall
**Delete the instances (CRs) from the cluster:**

```sh
kubectl delete -k config/samples/
```

**Delete the APIs(CRDs) from the cluster:**

```sh
make uninstall
```

**UnDeploy the controller from the cluster:**

```sh
make undeploy
```

## Project Distribution

Following are the steps to build the installer and distribute this project to users.

1. Build the installer for the image built and published in the registry:

```sh
make build-installer IMG=<some-registry>/appnet:tag
```

NOTE: The makefile target mentioned above generates an 'install.yaml'
file in the dist directory. This file contains all the resources built
with Kustomize, which are necessary to install this project without
its dependencies.

2. Using the installer

Users can just run kubectl apply -f <URL for YAML BUNDLE> to install the project, i.e.:

```sh
kubectl apply -f https://raw.githubusercontent.com/<org>/appnet/<tag or branch>/dist/install.yaml
```

## Contributing
// TODO(user): Add detailed information on how you would like others to contribute to this project

**NOTE:** Run `make help` for more information on all potential `make` targets

More information can be found via the [Kubebuilder Documentation](https://book.kubebuilder.io/introduction.html) -->

## Reference
Please consider citing our papers if you find AppNet related to your research.

```bibtex
@inproceedings{zhu2023application,
  title={Application Defined Networks},
  author={Zhu, Xiangfeng and Deng, Weixin and Liu, Banruo and Chen, Jingrong and Wu, Yongji and Anderson, Thomas and Krishnamurthy, Arvind and Mahajan, Ratul and Zhuo, Danyang},
  booktitle={Proceedings of the 22nd ACM Workshop on Hot Topics in Networks},
  pages={87--94},
  year={2023}
}

@inproceedings {zhu2025appnet,
  author = {Xiangfeng Zhu and Yuyao Wang and Banruo Liu and Yongtong Wu and Nikola Bojanic and Jingrong Chen and Gilbert Louis Bernstein and Arvind Krishnamurthy and Sam Kumar and Ratul Mahajan and Danyang Zhuo},
  title = {High-level Programming for Application Networks},
  booktitle = {22nd USENIX Symposium on Networked Systems Design and Implementation (NSDI 25)},
  year = {2025},
  address = {Philadelphia, PA},
  pages = {915--935},
}
```

## Contributors

AppNet is written and maintained by [Xiangfeng Zhu](https://xzhu27.me/), [Yuyao Wang](https://kristoff-starling.github.io/), [Yongtong Wu](https://jokerwyt.github.io/), [Nikola Bojanic](https://github.com/NikolaBo), and [Banruo Liu](https://github.com/livingshade).

If you have any questions or comments, please get in touch with Xiangfeng Zhu (xfzhu@cs.washington.edu).

<!-- 
## License

Copyright 2024.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
 -->
