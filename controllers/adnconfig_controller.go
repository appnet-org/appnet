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
	"strings"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	apiv1 "github.com/UWNetworksLab/app-defined-networks/api/v1"
)

// AdnconfigReconciler reconciles a Adnconfig object
type AdnconfigReconciler struct {
	client.Client
	Scheme *runtime.Scheme
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
		l.Error(err, "unable to fetch Adnconfig")
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	upstream_service := config.Spec.UpstreamService
	downstream_service := config.Spec.DownstreamService
	upstream_elements := strings.Split(config.Spec.UpstreamChain, "->")
	downstream_elements := strings.Split(config.Spec.DownstreamChain, "->")


	l.Info("Reconciling Adnconfig", "Name", config.Name, "Namespace", config.Namespace, "Upstream Service", upstream_service, "Downstream Service", downstream_service, "Upstream-side Elements", upstream_elements, "Downstream-side Elements", downstream_elements)

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *AdnconfigReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&apiv1.Adnconfig{}).
		Complete(r)
}
