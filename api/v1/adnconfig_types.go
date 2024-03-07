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

package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// NOTE: json tags are required.  Any new fields you add must have json tags for the fields to be serialized.

type ChainElement struct {
	Name       string            `json:"name"`
	File       string            `json:"file"`
	Parameters map[string]string `json:"parameters,omitempty"`
}

// AdnconfigSpec defines the desired state of Adnconfig
type AdnconfigSpec struct {
	// INSERT ADDITIONAL SPEC FIELDS - desired state of cluster
	// Important: Run "make" to regenerate code after modifying this file

	// Foo is an example field of Adnconfig. Edit adnconfig_types.go to remove/update
	// Type       string `json:"type"`
	// +kubebuilder:default:=true
	Safe            bool           `json:"safe,omitempty" default:"true"`
	AppName         string         `json:"appName"`
	AppManifestFile string         `json:"appManifestFile"`
	ClientService   string         `json:"clientService"`
	ServerService   string         `json:"serverService"`
	ClientChain     []ChainElement `json:"clientChain,omitempty"`
	ServerChain     []ChainElement `json:"serverChain,omitempty"`
	AnyChain        []ChainElement `json:"anyChain,omitempty"`
	PairChain       []ChainElement `json:"pairChain,omitempty"`
	Method          string         `json:"method"`
	Proto           string         `json:"proto"`
}

// AdnconfigStatus defines the observed state of Adnconfig
type AdnconfigStatus struct {
	// INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
	// Important: Run "make" to regenerate code after modifying this file
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// Adnconfig is the Schema for the adnconfigs API
type Adnconfig struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   AdnconfigSpec   `json:"spec,omitempty"`
	Status AdnconfigStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// AdnconfigList contains a list of Adnconfig
type AdnconfigList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Adnconfig `json:"items"`
}

func init() {
	SchemeBuilder.Register(&Adnconfig{}, &AdnconfigList{})
}
