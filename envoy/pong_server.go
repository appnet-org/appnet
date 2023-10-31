package main

import (
	"fmt"
	"log"
	"net"

	"golang.org/x/net/context"

	pong "github.com/UWNetworksLab/app-defined-networks/envoy/pong_pb"
	"google.golang.org/grpc"
)

type server struct {
	pong.Unimplemented
}

func (s *server) Echo(ctx context.Context, x *echo.Msg) (*echo.Msg, error) {
	log.Printf("got: [%s]", x.GetBody())
	return x, nil
}

func main() {
	lis, err := net.Listen("tcp", ":9000")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	fmt.Printf("Starting server at port 9000\n")

	echo.RegisterEchoServiceServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}