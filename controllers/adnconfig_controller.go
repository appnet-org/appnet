/*
Copyright 2023.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controllers

import (
	"context"
	"os"
	"os/exec"
	"strconv"
	"strings"
	// "fmt"
	"time"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	dockerTypes "github.com/docker/docker/api/types"
	dockerClient "github.com/docker/docker/client"

	apiv1 "github.com/UWNetworksLab/app-defined-networks/api/v1"
)

// AdnconfigReconciler reconciles a Adnconfig object
type AdnconfigReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

func GetProcessPID(processName string) (int, error) {
	// The command to run
	cmd := exec.Command("pgrep", "-f", processName)

	// Run the command and get its output
	output, err := cmd.Output()
	if err != nil {
		return 0, err
	}

	// Convert the output to a string
	pidStr := strings.TrimSpace(string(output))

	// Convert the PID string to an int
	pid, err := strconv.Atoi(pidStr)
	if err != nil {
		return 0, err
	}

	return pid, nil
}

func RunCommand(command string, args ...string) {
	// args = append(args, "sudo", "docker", "exec", "290defb90f05", )

	// Define the command to run
	cmd := exec.Command(command, args...)

	// Run the command and get its output
	// fmt.Println("Executing command:", cmd.String())
	_, err := cmd.Output()
	// fmt.Println(output)
	if err != nil {
		panic(err)
	}
}

func mrpc_init_setup(ctx context.Context, controlPlaneID string) {
	// Get server and client pids
	l := log.FromContext(ctx)
	serverPid, err := GetProcessPID("rpc_echo_server")
	if err != nil {
		l.Error(err, "Unable to find rpc_echo_server pid")
		return
	}
	clientPid, err := GetProcessPID("rpc_echo_client")
	if err != nil {
		l.Error(err, "Unable to find rpc_echo_client pid")
		return
	}

	err = os.Chdir("/users/xzhu/phoenix")
	if err != nil {
		l.Error(err, "Unable to change working directory")
		return
	}

	// RunCommand("cargo", "run", "--release", "--bin", "upgrade", "--", "--config", "experimental/mrpc/load-mrpc-plugins.toml")
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase1/receiver_attach.toml", "--pid", strconv.Itoa(serverPid), "--sid", "1")
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase1/ratelimit_attach.toml", "--pid", strconv.Itoa(clientPid), "--sid", "1")
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase1/logging_attach.toml", "--pid", strconv.Itoa(clientPid), "--sid", "1")
}

func mrpc_after_migration_unsafe(ctx context.Context, controlPlaneID string) {
	// Get server and client pids
	l := log.FromContext(ctx)
	serverPid, err := GetProcessPID("rpc_echo_server")
	if err != nil {
		l.Error(err, "Unable to find rpc_echo_server pid")
		return
	}
	clientPid, err := GetProcessPID("rpc_echo_client")
	if err != nil {
		l.Error(err, "Unable to find rpc_echo_client pid")
		return
	}

	err = os.Chdir("/users/xzhu/phoenix")
	if err != nil {
		l.Error(err, "Unable to change working directory")
		return
	}

	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase2/receiver_detach.toml", "--pid", strconv.Itoa(serverPid), "--sid", "1")
	time.Sleep(time.Second)
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase2/sender_attach.toml", "--pid", strconv.Itoa(clientPid), "--sid", "1")
}

func mrpc_after_migration_safe(ctx context.Context, controlPlaneID string) {
	// Get server and client pids
	l := log.FromContext(ctx)
	serverPid, err := GetProcessPID("rpc_echo_server")
	if err != nil {
		l.Error(err, "Unable to find rpc_echo_server pid")
		return
	}
	clientPid, err := GetProcessPID("rpc_echo_client")
	if err != nil {
		l.Error(err, "Unable to find rpc_echo_client pid")
		return
	}

	err = os.Chdir("/users/xzhu/phoenix")
	if err != nil {
		l.Error(err, "Unable to change working directory")
		return
	}

	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase2/sender_attach.toml", "--pid", strconv.Itoa(clientPid), "--sid", "1")
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase2/receiver_detach.toml", "--pid", strconv.Itoa(serverPid), "--sid", "1")
}

func remove_all_engines(ctx context.Context, controlPlaneID string) {
	// Get server and client pids
	l := log.FromContext(ctx)
	// _, err := GetProcessPID("rpc_echo_client2")
	clientPid, err := GetProcessPID("rpc_echo_client")
	if err != nil {
		l.Error(err, "Unable to find rpc_echo_client pid")
		return
	}

	err = os.Chdir("/users/xzhu/phoenix")
	if err != nil {
		l.Error(err, "Unable to change working directory")
		return
	}
	// RunCommand("bash", "remove_engines.sh", controlPlaneID)
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase3/logging_detach.toml", "--pid", strconv.Itoa(clientPid), "--sid", "1")
	time.Sleep(time.Second)
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase3/sender_detach.toml", "--pid", strconv.Itoa(clientPid), "--sid", "1")
	// time.Sleep(2*time.Second)
	RunCommand("docker", "exec", controlPlaneID, "cargo", "run", "--release", "--bin", "addonctl", "--", "--config", "eval/policy/chain/phase3/ratelimit_detach.toml", "--pid", strconv.Itoa(clientPid), "--sid", "1")
}

func getControlPlaneID(ctx context.Context) string {
	cli, err := dockerClient.NewClientWithOpts(dockerClient.FromEnv)
	if err != nil {
		panic(err)
	}

	// Get the container name from user input or from a variable
	containerName := "phoenixos"

	// List all running containers with their IDs and names
	containers, err := cli.ContainerList(ctx, dockerTypes.ContainerListOptions{})
	if err != nil {
		panic(err)
	}

	// for _, container := range containers {
	//     fmt.Printf("%s %s\n", container.ID[:10], container.Image)
	// }

	// Loop through the containers to find the one with the matching name
	var containerID string
	for _, container := range containers {
		if container.Image == containerName {
			containerID = container.ID[:10]
			break
		}
	}

	// // Print the ID of the matching container
	// fmt.Println("Printing contaier ID")
	// fmt.Println(containerID)

	return containerID
}

//+kubebuilder:rbac:groups=api.core.adn.io,resources=adnconfigs,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=api.core.adn.io,resources=adnconfigs/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=api.core.adn.io,resources=adnconfigs/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the Adnconfig object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.14.1/pkg/reconcile
func (r *AdnconfigReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	l := log.FromContext(ctx)

	controlPlaneID := getControlPlaneID(ctx)
	// TODO: add logic here
	config := &apiv1.Adnconfig{}
	err := r.Get(ctx, req.NamespacedName, config)
	if err != nil {
		// l.Error(err, "unable to fetch Adnconfig")
		l.Info("calling remove_all_engines")
		remove_all_engines(ctx, controlPlaneID)
		l.Info("Reconciliation finished!")
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	upstream_service := config.Spec.UpstreamService
	downstream_service := config.Spec.DownstreamService
	upstream_elements := strings.Split(config.Spec.UpstreamChain, "->")
	downstream_elements := strings.Split(config.Spec.DownstreamChain, "->")

	// Call addonctl
	// l.Info("Request is %v", req)
	l.Info("Reconciling Adnconfig", "Name", config.Name, "Namespace", config.Namespace, "Upstream Service", upstream_service, "Downstream Service", downstream_service, "Upstream-side Elements", upstream_elements, "Downstream-side Elements", downstream_elements)
	// l.Info("Length of upstream_elements is", len(upstream_elements))
	if len(upstream_elements) == 2 {
		l.Info("calling mrpc_init_setup")
		mrpc_init_setup(ctx, controlPlaneID)
	} else if len(upstream_elements) == 3 && strings.Contains(config.Spec.UpstreamChain, "unsafe") {
		l.Info("calling mrpc_after_migration_unsafe")
		mrpc_after_migration_unsafe(ctx, controlPlaneID)
	} else if len(upstream_elements) == 3 && strings.Contains(config.Spec.UpstreamChain, "safe") {
		l.Info("calling mrpc_after_migration_safe")
		mrpc_after_migration_safe(ctx, controlPlaneID)
	}

	// TODO: add detach logic
	l.Info("Reconciliation finished!")
	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *AdnconfigReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&apiv1.Adnconfig{}).
		Complete(r)
}
