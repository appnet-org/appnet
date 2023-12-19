package main

import (
	"fmt"
	"log"
	"net"

	"golang.org/x/net/context"

	// "github.com/UWNetworksLab/adn-controller/grpc/interceptors/null"
	// "github.com/UWNetworksLab/adn-controller/grpc/interceptors/acl"

	echo "github.com/UWNetworksLab/adn-controller/grpc/pb"
	"google.golang.org/grpc"
)

type server struct {
	echo.UnimplementedEchoServiceServer
}

func (s *server) Echo(ctx context.Context, x *echo.Msg) (*echo.Msg, error) {
	log.Printf("got: [%s]", x.GetBody())

	appendedBody := x.GetBody() + "1"
	msg := &echo.Msg{
		Body: appendedBody,
	}
	return msg, nil
}

func main() {
	lis, err := net.Listen("tcp", ":9000")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	// nullOpts := []null.CallOption{null.WithMessage("Null"),}
	// aclOpts := []acl.CallOption{acl.WithContent("server"),}

	s := grpc.NewServer(
		// grpc.ChainUnaryInterceptor(
		// 	null.NullServer(nullOpts...),
		// 	acl.ACLServer(aclOpts...),
		// ),
	)
	fmt.Printf("Starting server pod at port 9000\n")

	echo.RegisterEchoServiceServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
