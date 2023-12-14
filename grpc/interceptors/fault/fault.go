package fault

import (
	"log"
	"math/rand"
	"time"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"golang.org/x/net/context"

	"google.golang.org/grpc"
)



func FaultClient(optFuncs ...CallOption) grpc.UnaryClientInterceptor {
	// Combine the default options with any user-provided options.
	intOpts := reuseOrNewWithCallOptions(defaultOptions, optFuncs)

	return func(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
		// Split the gRPC CallOptions into two sets: gRPC-specific options and null options.
		grpcOpts, nullOptions := filterCallOptions(opts)

		// Combine the internal options with the null options.
		callOpts := reuseOrNewWithCallOptions(intOpts, nullOptions)
		log.Println("Hello from FaultUnaryClientInterceptor")

		// Generate a random float between 0 and 1.
		rand.Seed(time.Now().UnixNano())
		p := rand.Float64()
		
		if p <= callOpts.abortProbability {
			return status.Error(codes.Aborted, "request aborted by fault injection.")
		}
		
		err := invoker(ctx, method, req, reply, cc, grpcOpts...)
		return err
	}
}

func FaultServer(optFuncs ...CallOption) grpc.UnaryServerInterceptor {
	// Combine the default options with any user-provided options.
	intOpts := reuseOrNewWithCallOptions(defaultOptions, optFuncs)

	return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		log.Println("Running FaultUnaryServerInterceptor")

		// Generate a random float between 0 and 1.
		rand.Seed(time.Now().UnixNano())
		p := rand.Float64()
		
		if p <= intOpts.abortProbability {
			return nil, status.Error(codes.Aborted, "request aborted by fault injection.")
		}

		return handler(ctx, req)
	}
}

