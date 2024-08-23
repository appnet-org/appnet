package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"golang.org/x/exp/rand"
)

func handleRequest(w http.ResponseWriter, r *http.Request) {
	serviceName, ok := r.URL.Query()["service-name"]
	replicaIDsParam, ok2 := r.URL.Query()["replica-ids"]

	// Log the incoming request
	fmt.Printf("Received request: %s %s\n", r.Method, r.URL.String())

	if !ok || len(serviceName[0]) < 1 || !ok2 || len(replicaIDsParam[0]) < 1 {
		http.Error(w, "Missing service name or replica id parameter", http.StatusBadRequest)
		return
	}

	// Split the replica IDs based on commas
	replicaIDs := strings.Split(replicaIDsParam[0], ",")

	// Initialize the response map
	response := make(map[string]interface{})

	// Get the current timestamp
	timestamp := float64(time.Now().UnixNano()) / 1e9

	// Seed the random number generator
	rand.Seed(42)

	// Loop through the replica IDs and add each with its load and timestamp
	for _, replicaID := range replicaIDs {
		// Generate a random load between 1 and 10
		load := rand.Intn(10) + 1

		response[replicaID] = map[string]interface{}{
			"load":      load,
			"timestamp": timestamp,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func startHTTPServer() {
	http.HandleFunc("/getLoadInfo", handleRequest)
	fmt.Println("Starting HTTP server on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func main() {
	// Start the HTTP server
	startHTTPServer()

	// Keep the program running
	for {
		time.Sleep(time.Second)
	}
}
