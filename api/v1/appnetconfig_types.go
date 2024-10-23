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

package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// EDIT THIS FILE!  THIS IS SCAFFOLDING FOR YOU TO OWN!
// NOTE: json tags are required.  Any new fields you add must have json tags for the fields to be serialized.
type ChainElement struct {
	Name string `json:"name"`
	File string `json:"file"`
	// +kubebuilder:default=true
	Upgrade    bool              `json:"upgrade,omitempty"`
	Parameters map[string]string `json:"parameters,omitempty"`
}

// AppNetConfigSpec defines the desired state of AppNetConfig
type AppNetConfigSpec struct {
	// INSERT ADDITIONAL SPEC FIELDS - desired state of cluster
	// Important: Run "make" to regenerate code after modifying this file

	Safe             bool           `json:"safe,omitempty" default:"true"`
	Processors       []string       `json:"processors"`
	AppName          string         `json:"appName"`
	AppManifestFile  string         `json:"appManifestFile"`
	ClientService    string         `json:"clientService"`
	ServerService    string         `json:"serverService"`
	ClientChain      []ChainElement `json:"clientChain,omitempty"`
	ServerChain      []ChainElement `json:"serverChain,omitempty"`
	AnyChain         []ChainElement `json:"anyChain,omitempty"`
	PairChain        []ChainElement `json:"pairChain,omitempty"`
	Method           string         `json:"method"`
	Proto            string         `json:"proto"`
	ProtoModName     string         `json:"protoModName,omitempty"`
	ProtoModLocation string         `json:"protoModLocation,omitempty"`
}

// AppNetConfigStatus defines the observed state of AppNetConfig
type AppNetConfigStatus struct {
	// INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
	// Important: Run "make" to regenerate code after modifying this file
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// AppNetConfig is the Schema for the appnetconfigs API
type AppNetConfig struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   AppNetConfigSpec   `json:"spec,omitempty"`
	Status AppNetConfigStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// AppNetConfigList contains a list of AppNetConfig
type AppNetConfigList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []AppNetConfig `json:"items"`
}

func init() {
	SchemeBuilder.Register(&AppNetConfig{}, &AppNetConfigList{})
}
