package services

import (
	"fmt"

	"google.golang.org/grpc"
)

// dial creates a new gRPC client connection to the specified address and returns a client connection object.
func dial(addr string) *grpc.ClientConn {
	// Define gRPC dial options for the client connection.
	opts := []grpc.DialOption{
		grpc.WithInsecure(),
	}

	// Create a new gRPC client connection to the specified address using the dial options.
	conn, err := grpc.Dial(addr, opts...)
	if err != nil {
		// If there was an error creating the client connection, panic with an error message.
		panic(fmt.Sprintf("ERROR: dial error: %v", err))
	}

	// Return the created client connection object.
	return conn
}

