/*
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
*/

package controller

import (
	"context"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"sync"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	apiv1 "github.com/appnet-org/appnet/api/v1"
)

// AppNetConfigReconciler reconciles a AppNetConfig object
type AppNetConfigReconciler struct {
	client.Client
	Scheme  *runtime.Scheme
	mu      sync.Mutex
	Version int
}

//+kubebuilder:rbac:groups=api.core.appnet.io,resources=appnetconfigs,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=api.core.appnet.io,resources=appnetconfigs/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=api.core.appnet.io,resources=appnetconfigs/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the AppNetConfig object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.17.0/pkg/reconcile
func (r *AppNetConfigReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	_ = log.FromContext(ctx)

	l := log.FromContext(ctx)

	// TODO: add logic here
	config := &apiv1.AppNetConfig{}
	err := r.Get(ctx, req.NamespacedName, config)
	if err != nil {
		// For AppNet resource deletion
		l.Info("Deleting AppNetConfig...")

		// TODO: Only delete the envoy filters that are associated with this AppNetConfig
		exec.Command("kubectl", "delete", "envoyfilters", "--all").CombinedOutput()
		exec.Command("istioctl", "experimental", "waypoint", "delete", "--all").CombinedOutput()
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	backend := config.Spec.Backend

	// temporary fix for sidecar backend
	if backend == "sidecar" {
		backend = "envoy"
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

	proto_mod_name := config.Spec.ProtoModName
	proto_mod_location := config.Spec.ProtoModLocation

	safe := config.Spec.Safe

	r.mu.Lock()
	r.Version++
	currentVersion := r.Version
	r.mu.Unlock()

	// Call addonctl
	l.Info("Reconciling AppNetConfig", "Safe", safe, "Name", config.Name, "Namespace", config.Namespace, "RPC Method", method,
		"Backend:", backend, "Client Service", client_service, "Server Service", server_service, "client-side Elements", client_elements,
		"server-side Elements", server_elements, "unconstraint Elements", any_elements, "pair Elements", pair_elements)

	l.Info("Reconciling AppNetConfig", "Safe", safe, "Name", config.Name, "Proto module name", proto_mod_name, "Proto Module location", proto_mod_location)

	ConvertToAppNetSpec(app_name, backend, app_manifest_file, client_service, server_service, method, proto, "config.yaml",
		proto_mod_name, proto_mod_location, client_elements, server_elements, any_elements, pair_elements)

	compilerDir := filepath.Join(os.Getenv("APPNET_DIR"), "compiler/compiler")

	compile_cmd := exec.Command("python", filepath.Join(compilerDir, "main.py"), "-s", "config.yaml", "-b", backend, "-t", strconv.Itoa(currentVersion))
	compile_output, compile_err := compile_cmd.CombinedOutput()

	// Check if there was an error running the command
	if compile_err != nil {
		l.Info("Reconciling AppNetConfig", "Error running compiler: %s\nOutput:\n%s\n", compile_err, string(compile_output))
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	l.Info("All elements compiled successfully - deploying to envoy")

	// TODO: temp hack
	if currentVersion == 1 {
		kubectl_cmd := exec.Command("kubectl", "apply", "-f", strings.ReplaceAll(filepath.Join(compilerDir, "graph/generated/APP-deploy/install.yml"), "APP", app_name))
		kubectl_output, kubectl_err := kubectl_cmd.CombinedOutput()

		// Check if there was an error running the command
		if kubectl_err != nil {
			l.Info("Reconciling AppNetConfig", "Error running kubectl: %s\nOutput:\n%s\n", kubectl_err, string(kubectl_output))
			return ctrl.Result{}, client.IgnoreNotFound(err)
		}
	}

	// Deploy waypoint proxies
	if backend == "ambient" {
		// XZ: Temp hack to wait for all pods running
		waypoint_cmd := exec.Command("bash", strings.ReplaceAll(filepath.Join(compilerDir, "graph/generated/APP-deploy/waypoint_create.sh"), "APP", app_name))
		waypoint_output, waypoint_err := waypoint_cmd.CombinedOutput()

		// Check if there was an error running the command
		if waypoint_err != nil {
			l.Info("Reconciling AppNetConfig", "Error running istioctl waypoint: %s\nOutput:\n%s\n", waypoint_err, string(waypoint_output))
			return ctrl.Result{}, client.IgnoreNotFound(err)
		}

		// Attach volume to waypoint
		waypoint_name := find_waypoint_name(strings.ReplaceAll(filepath.Join(compilerDir, "graph/generated/APP-deploy/waypoint_create.sh"), "APP", app_name))
		l.Info("Reconciling AppNetConfig", server_service, waypoint_name)
		attach_volume_to_waypoint(server_service, waypoint_name)
	}

	if backend != "grpc" {
		attach_cmd := exec.Command("kubectl", "apply", "-f", strings.ReplaceAll(filepath.Join(compilerDir, "graph/generated/APP-deploy/attach_all_elements.yml"), "APP", app_name))
		attach_output, attach_err := attach_cmd.CombinedOutput()

		// Check if there was an error running the command
		if attach_err != nil {
			l.Info("Reconciling AppNetConfig", "Error running kubectl: %s\nOutput:\n%s\n", attach_err, string(attach_output))
			return ctrl.Result{}, client.IgnoreNotFound(err)
		}
	}

	l.Info("All elemenets deployed - Reconciliation finished!")

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *AppNetConfigReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&apiv1.AppNetConfig{}).
		Complete(r)
}
