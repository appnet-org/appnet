# gRPC echo server

This is a simple Echo server built using Go and gRPC.

## Run as docker container 
To run the server as a Docker container, follow these steps:
- Change ":9000" to "server:9000" in frontend.go (this is only required for Docker deployments).
- `docker build --tag echo-frontend -f Dockerfile-frontend .`
- `docker build --tag echo-server -f Dockerfile-server  .`
- `docker network create test`
- `docker run --rm -d --net test -p 9000:9000 --name server echo-server`
- `docker run --rm -d --net test -p 8080:8080 --name frontend echo-frontend`
- `curl http://localhost:8080/echo`

## Push docker container
- Change ":9000" to "echo-server:9000" in frontend.go (this is only required for Kubernetes deployments).
- `docker build --tag echo-frontend -f Dockerfile-frontend .`
- `docker build --tag echo-server -f Dockerfile-server .`
- `docker tag echo-frontend xzhu0027/echo-frontend-grpc`
- `docker push xzhu0027/echo-frontend-grpc`
- `docker tag echo-server xzhu0027/echo-server-grpc`
- `docker push xzhu0027/echo-server-grpc`

## Note
Work in progress. Potential issues:
- Shared state in client interceptors. Each request will go through a fresh instance of the interceptor. It's hard to maintain a shared variable. I had to use a global variable with mutex (this might have performance penalty. To be tested). Server-side does not have this problem.