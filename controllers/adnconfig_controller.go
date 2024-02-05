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
	// "os"
	"os/exec"
	"strconv"
	"strings"
	// "fmt"
	// "time"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	// dockerTypes "github.com/docker/docker/api/types"
	// dockerClient "github.com/docker/docker/client"

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

	// TODO: add logic here
	config := &apiv1.Adnconfig{}
	err := r.Get(ctx, req.NamespacedName, config)
	if err != nil {
		// This is for adn resource deletion
		// l.Error(err, "unable to fetch Adnconfig")
		// l.Info("calling remove_all_engines")
		// l.Info("Reconciling Adnconfig")
		// remove_all_engines(ctx, controlPlaneID)
		// l.Info("Reconciliation finished!")
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	client_service := config.Spec.ClientService
	server_service := config.Spec.ServerService
	client_elements := strings.Split(config.Spec.ClientChain, "->")
	server_elements := strings.Split(config.Spec.ServerChain, "->")
	any_elements := strings.Split(config.Spec.AnyChain, "->")
	pair_elements := strings.Split(config.Spec.PairChain, "->")
	method := config.Spec.Method

	safe := config.Spec.Safe

	// Call addonctl
	l.Info("Reconciling Adnconfig", "Safe", safe, "Name", config.Name, "Namespace", config.Namespace, "RPC Method", method,
		"Client Service", client_service, "Server Service", server_service, "client-side Elements", client_elements,
		"server-side Elements", server_elements, "unconstraint Elements", any_elements, "pair Elements", pair_elements)
	// l.Info("Length of upstream_elements is", len(upstream_elements))
	// if len(upstream_elements) == 2 {
	// 	// l.Info("calling mrpc_init_setup")
	// 	mrpc_init_setup(ctx, controlPlaneID)
	// } else if len(upstream_elements) == 3 && safe == false {
	// 	// l.Info("calling mrpc_after_migration_unsafe")
	// 	mrpc_after_migration_unsafe(ctx, controlPlaneID)
	// } else if len(upstream_elements) == 3 && safe == true {
	// 	// l.Info("calling mrpc_after_migration_safe")
	// 	mrpc_after_migration_safe(ctx, controlPlaneID)
	// }

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
