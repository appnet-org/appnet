module github.com/UWNetworksLab/meshinsight/meshinsight/profiler/benchmark/echo_server_grpc

go 1.18

require (
	golang.org/x/net v0.7.0
	google.golang.org/grpc v1.53.0
	google.golang.org/protobuf v1.28.1
)

require (
	github.com/golang/protobuf v1.5.2 // indirect
	golang.org/x/sys v0.5.0 // indirect
	golang.org/x/text v0.7.0 // indirect
	google.golang.org/genproto v0.0.0-20230223222841-637eb2293923 // indirect
)

replace github.com/UWNetworksLab/app-defined-networks/envoy/ping_pb => ./ping_pb

replace github.com/UWNetworksLab/app-defined-networks/envoy/pong_pb => ./pong_pb
