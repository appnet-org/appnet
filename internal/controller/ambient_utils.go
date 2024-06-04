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
	"bufio"
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"time"

	corev1 "k8s.io/api/core/v1"
	// appsv1 "k8s.io/api/apps/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

func find_waypoint_name(file_name string) string {
	file, err := os.Open(file_name)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return ""
	}
	defer file.Close()

	// Create a regular expression to match the service account
	re := regexp.MustCompile(`--name\s+(\S+)`)

	// Create a scanner to read the file line by line
	scanner := bufio.NewScanner(file)

	// Iterate through each line of the file
	for scanner.Scan() {
		line := scanner.Text()
		// Check if the line contains the service account
		match := re.FindStringSubmatch(line)
		if len(match) > 1 {
			// Extract the service account from the matched line
			waypoint := match[1]
			return waypoint
		}
	}

	// Check for scanner errors
	if err := scanner.Err(); err != nil {
		return ""
	}

	return ""
}

func attach_volume_to_waypoint(service_name, waypoint_name string) {
	// Set up kubeconfig path
	var k8sconfig *string
	if home := homedir.HomeDir(); home != "" {
		k8sconfig = flag.String("k8sconfig", filepath.Join(home, ".kube", "config"), "(optional) absolute path to the kubeconfig file")
	} else {
		k8sconfig = flag.String("k8sconfig", "", "absolute path to the k8sconfig file")
	}
	flag.Parse()

	// Use the current context in kubeconfig
	config, err := clientcmd.BuildConfigFromFlags("", *k8sconfig)
	if err != nil {
		panic(err.Error())
	}

	// Create the clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}

	// Set deployment details
	namespace := "default"
	deploymentName := waypoint_name
	pvcName := service_name + "-pvc"
	mountPath := "/data"

	maxAttempts := 20

	// Retry on failure (sometimes deployment changes wjile updating)
	for attempts := 0; attempts < maxAttempts; attempts++ {
		// Get the specified deployment
		deployment, err := clientset.AppsV1().Deployments(namespace).Get(context.TODO(), deploymentName, metav1.GetOptions{})
		if err != nil {
			fmt.Printf("Attempt %d: failed to get deployment: %v\n", attempts+1, err)
			time.Sleep(2 * time.Second) // Wait before retrying
			continue
		}

		// Define the volume and volume mount
		volume := corev1.Volume{
			Name: service_name + "-storage",
			VolumeSource: corev1.VolumeSource{
				PersistentVolumeClaim: &corev1.PersistentVolumeClaimVolumeSource{
					ClaimName: pvcName,
				},
			},
		}
		volumeMount := corev1.VolumeMount{
			Name:      service_name + "-storage",
			MountPath: mountPath,
		}

		// Check if the volume and volume mount already exist to avoid duplicates
		volumeExists := false
		for _, v := range deployment.Spec.Template.Spec.Volumes {
			if v.Name == volume.Name {
				volumeExists = true
				break
			}
		}
		if !volumeExists {
			deployment.Spec.Template.Spec.Volumes = append(deployment.Spec.Template.Spec.Volumes, volume)
		}

		for i := range deployment.Spec.Template.Spec.Containers {
			volumeMountExists := false
			for _, vm := range deployment.Spec.Template.Spec.Containers[i].VolumeMounts {
				if vm.Name == volumeMount.Name {
					volumeMountExists = true
					break
				}
			}
			if !volumeMountExists {
				deployment.Spec.Template.Spec.Containers[i].VolumeMounts = append(deployment.Spec.Template.Spec.Containers[i].VolumeMounts, volumeMount)
			}
		}

		// Update the deployment
		_, err = clientset.AppsV1().Deployments(namespace).Update(context.TODO(), deployment, metav1.UpdateOptions{})
		if err != nil {
			if errors.IsConflict(err) {
				// If there's a conflict, retry the operation
				continue
			} else {
				panic(err.Error())
			}
		}
		break
	}
}
