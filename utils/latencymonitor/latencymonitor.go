package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

func handleRequest(w http.ResponseWriter, r *http.Request) {
	serviceName, ok := r.URL.Query()["service-name"]
	replicaIDs, ok2 := r.URL.Query()["replica-ids"]

	if !ok || len(serviceName[0]) < 1 || !ok2 || len(replicaIDs[0]) < 1 {
		http.Error(w, "Missing service name or replica id parameter", http.StatusBadRequest)
		return
	}

	response := map[string]int{
		"load": 1,
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
