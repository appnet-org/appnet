package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strconv"
	"sync"
	"time"

	"gopkg.in/yaml.v2"

	"github.com/fsnotify/fsnotify"
)

type Shard struct {
	ShardID string `yaml:"shard_id"`
	Role    string `yaml:"role"`
	Range   []int  `yaml:"range"`
}

type Replica struct {
	ReplicaID int     `yaml:"replica_id"`
	Shards    []Shard `yaml:"shards"`
}

type Service struct {
	Name     string    `yaml:"name"`
	Replicas []Replica `yaml:"replicas"`
}

type Services struct {
	Services []Service `yaml:"services"`
}

var (
	services    Services
	servicesMut sync.RWMutex
)

func readYAMLFile(filename string) (Services, error) {
	var services Services

	data, err := ioutil.ReadFile(filename)
	if err != nil {
		return services, err
	}

	err = yaml.Unmarshal(data, &services)
	if err != nil {
		return services, err
	}

	return services, nil
}

func watchFile(filename string, onUpdate func(Services)) {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()

	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Op&fsnotify.Write == fsnotify.Write {
					fmt.Println("File modified:", event.Name)
					services, err := readYAMLFile(filename)
					if err != nil {
						log.Println("Error reading YAML file:", err)
					} else {
						onUpdate(services)
					}
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				log.Println("Error:", err)
			}
		}
	}()

	err = watcher.Add(filename)
	if err != nil {
		log.Fatal(err)
	}

	// Keep the watcher running
	select {}
}

func updateServices(newServices Services) {
	servicesMut.Lock()
	defer servicesMut.Unlock()
	services = newServices
	fmt.Printf("Updated Services: %+v\n", services)
}

func getReplicaIDByServiceAndKey(serviceName string, key int) ([]int, error) {
	servicesMut.RLock()
	defer servicesMut.RUnlock()

	var replicaIDs []int

	for _, service := range services.Services {
		if service.Name == serviceName {
			for _, replica := range service.Replicas {
				for _, shard := range replica.Shards {
					if key >= shard.Range[0] && key <= shard.Range[1] {
						replicaIDs = append(replicaIDs, replica.ReplicaID)
					}
				}
			}
		}
	}

	if len(replicaIDs) == 0 {
		return nil, fmt.Errorf("no replicas found for service %s and key %d", serviceName, key)
	}

	return replicaIDs, nil
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	keys, ok := r.URL.Query()["key"]
	serviceName, ok2 := r.URL.Query()["service"]

	if !ok || len(keys[0]) < 1 || !ok2 || len(serviceName[0]) < 1 {
		http.Error(w, "Missing key or service parameter", http.StatusBadRequest)
		return
	}

	key, err := strconv.Atoi(keys[0])
	if err != nil {
		http.Error(w, "Invalid key parameter", http.StatusBadRequest)
		return
	}

	replicaIDs, err := getReplicaIDByServiceAndKey(serviceName[0], key)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	response := map[string][]int{
		"replica_id": replicaIDs,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func startHTTPServer() {
	// curl "http://localhost:8080/getReplica?key=23&service=ServiceA"
	http.HandleFunc("/getReplica", handleRequest)
	fmt.Println("Starting HTTP server on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func main() {
	filename := "/data/example_shard.yaml"

	// Initial read
	initialServices, err := readYAMLFile(filename)
	if err != nil {
		log.Fatalf("Error reading YAML file: %v", err)
	}
	updateServices(initialServices)

	// Watch the file for changes
	go watchFile(filename, updateServices)

	// Start the HTTP server
	startHTTPServer()

	// Keep the program running
	for {
		time.Sleep(time.Second)
	}
}
