package services

import (
	"context"
	"fmt"
	"log"
	"net"

	"github.com/UWNetworksLab/app-defined-networks/envoy/ping_pb"
	"github.com/UWNetworksLab/app-defined-networks/envoy/pong_pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/proto"
)

// Ping implements the ping service
type Ping struct {
	name string
	port int
	ping.PingServiceServer
	pongClient      pong.PongServiceClient
}

// NewPing returns a new server
func NewPing(name string, pingPort int, pongaddr string) *Ping {
	return &Ping{
		name:      name,
		port:      pingPort,
		pongClient:      pong.NewPongServiceClient(dial(pongaddr)),
	}
}

// Run starts the Ping gRPC server and listens for incoming requests.
// It returns an error if the server fails to start or encounters an error.
func (s *Ping) Run() error {
	// Create a new gRPC server instance.
	srv := grpc.NewServer()

	// Register the Ping server implementation with the gRPC server.
	ping.RegisterPingServiceServer(srv, s)

	// Create a TCP listener that listens for incoming requests on the specified port.
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	// (Optional) Log a message indicating that the server is running and listening on the specified port.
	log.Printf("ping server running at port: %d", s.port)

	// Start serving incoming requests using the registered implementation.
	return srv.Serve(lis)
}

func (s *Ping) Ping(ctx context.Context, req *ping.PingRequest) (*ping.PingResponse, error) {
	pingResponse := &ping.GetPingResponse{body: "ping response"}

	return pingResponse, err
}

func (s *Ping) PingEcho(ctx context.Context, req *ping.PingEchoRequest) (*ping.PingEchoResponse, error) {

	body := req.GetBody()
	pingEchoResponse := &ping.PingEchoResponse{body: body}

	return pingEchoResponse, err
}


// PostPing adds or updates the pings of a restaurant in the in-memory dataStore.
func (s *Ping) PingPong(ctx context.Context, req *ping.PingPongRequest) (*ping.PingPongResponse, error) {
	ctx := r.Context()

	req := &pong.PongRequest{body: "ping pong request"}
	reply, err := s.pongClient.pong(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	pingPongResponse := &ping.PingPongResponse{body: "ping pong response"}

	// Return the response object and any error.
	return pingPongResponse, err
}

