package null

import (
	"log"

	"golang.org/x/net/context"

	"google.golang.org/grpc"
)

// Hello is a client-side unary interceptor function that logs a greeting message.
func NullClient(optFuncs ...CallOption) grpc.UnaryClientInterceptor {
	// Combine the default options with any user-provided options.
	intOpts := reuseOrNewWithCallOptions(defaultOptions, optFuncs)

	return func(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
		// Split the gRPC CallOptions into two sets: gRPC-specific options and null options.
		grpcOpts, nullOptions := filterCallOptions(opts)

		// Combine the internal options with the null options.
		callOpts := reuseOrNewWithCallOptions(intOpts, nullOptions)
		
		log.Printf("Running %sUnaryClientInterceptor\n", callOpts.message)
		err := invoker(ctx, method, req, reply, cc, grpcOpts...)
		return err
	}
}

func NullServer(optFuncs ...CallOption) grpc.UnaryServerInterceptor {
	// Combine the default options with any user-provided options.
	intOpts := reuseOrNewWithCallOptions(defaultOptions, optFuncs)

	return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		log.Printf("Running %sUnaryClientInterceptor\n", intOpts.message)
		return handler(ctx, req)
	}
}

