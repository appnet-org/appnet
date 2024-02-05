## Miscellaneous Scripts

- `k8s_setup.sh`: Set up the Kubernetes (for control plane)
- `k8s_setup_worker.sh`: Set up the Kubernetes (for worker nodes.)
    - Need to run the join command manually (run `kubeadm token create --print-join-command` on the control plane node.)
- `istio_install_sidecar.sh`: Install Istio with sidecar mode
- `istio_install_ambient.sh`: Install Istio with ambient mode
- `linux_setup.sh`: To get consistency result on Linux.

