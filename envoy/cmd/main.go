package main

import (
	"flag"
	"log"
	"os"

	services "github.com/UWNetworksLab/adn-controller/envoy/services"
)

type server interface {
	Run() error
}

func main() {
	// Define the flags to specify port numbers and addresses
	var (
		frontendPort     = flag.Int("frontend", 8080, "frontend server port")
		pingPort       = flag.Int("pingport", 8081, "ping service port")
		pongPort       = flag.Int("pongport", 8082, "pong service port")

		// pingAddr      = flag.String("pingaddr", "ping:8081", "ping service address")
		// pongAddr      = flag.String("pongaddr", "pong:8082", "pong service addr")

		pingAddr      = flag.String("pingaddr", ":8081", "ping service address")
		pongAddr      = flag.String("pongaddr", ":8082", "pong service addr")
	)

	// Parse the flags
	flag.Parse()

	var srv server
	var cmd = os.Args[1]

	// Switch statement to create the correct service based on the command
	switch cmd {
	case "frontend":
		// Create a new frontend service with the specified ports and addresses
		srv = services.NewFrontend(
			*frontendPort,
			*pingAddr,
			*pongAddr,
		)
	case "ping":
		// Create a new ping service with the specified port
		srv = services.NewPing(
			"ping",
			*pingPort,
			*pongAddr,
		)
	case "pong":
		// Create a new pong service with the specified port
		srv = services.NewPong(
			"pong",
			*pongPort,
		)
	default:
		// If an unknown command is provided, log an error and exit
		log.Fatalf("unknown cmd: %s", cmd)
	}

	// Start the server and log any errors that occur
	if err := srv.Run(); err != nil {
		log.Fatalf("run %s error: %v", cmd, err)
	}
}
