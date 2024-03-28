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
	"path/filepath"
	"strconv"
	"strings"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	apiv1 "github.com/appnet-org/appnet/api/v1"
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
		// For adn resource deletion
		l.Info("Deleting Adnconfig")

		// TODO: Only delete the envoy filters that are associated with this adnconfig
		exec.Command("kubectl", "delete", "envoyfilters", "--all").CombinedOutput()
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	client_service := config.Spec.ClientService
	server_service := config.Spec.ServerService
	client_elements := config.Spec.ClientChain
	server_elements := config.Spec.ServerChain
	any_elements := config.Spec.AnyChain
	pair_elements := config.Spec.PairChain
	method := config.Spec.Method
	proto := config.Spec.Proto
	app_name := config.Spec.AppName
	app_manifest_file := config.Spec.AppManifestFile

	safe := config.Spec.Safe

	// Call addonctl
	l.Info("Reconciling Adnconfig", "Safe", safe, "Name", config.Name, "Namespace", config.Namespace, "RPC Method", method,
		"Client Service", client_service, "Server Service", server_service, "client-side Elements", client_elements,
		"server-side Elements", server_elements, "unconstraint Elements", any_elements, "pair Elements", pair_elements)

	ConvertToADNSpec(app_name, app_manifest_file, client_service, server_service, method, proto, "config.yaml", client_elements, server_elements,
		any_elements, pair_elements)

	compilerDir := filepath.Join(os.Getenv("ADN_DIR"), "compiler/compiler")

	compile_cmd := exec.Command("python3.10", filepath.Join(compilerDir, "main.py"), "-s", "config.yaml", "-b", "envoy")
	compile_output, compile_err := compile_cmd.CombinedOutput()

	// Check if there was an error running the command
	if compile_err != nil {
		l.Info("Reconciling Adnconfig", "Error running compiler: %s\nOutput:\n%s\n", compile_err, string(compile_output))
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	l.Info("All elements compiled successfully - deploying to envoy")

	kubectl_cmd := exec.Command("kubectl", "apply", "-Rf", strings.ReplaceAll(filepath.Join(compilerDir, "graph/generated/APP-deploy"), "APP", app_name))
	kubectl_output, kubectl_err := kubectl_cmd.CombinedOutput()

	// Check if there was an error running the command
	if kubectl_err != nil {
		l.Info("Reconciling Adnconfig", "Error running kubectl: %s\nOutput:\n%s\n", kubectl_err, string(kubectl_output))
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	l.Info("All elemenets deployed - Reconciliation finished!")
	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *AdnconfigReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&apiv1.Adnconfig{}).
		Complete(r)
}
