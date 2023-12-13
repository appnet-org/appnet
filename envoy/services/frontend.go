package services

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	ping "github.com/UWNetworksLab/adn-controller/envoy/ping_pb"
	pong "github.com/UWNetworksLab/adn-controller/envoy/pong_pb"
)

// Frontend implements a service that acts as an interface to interact with different microservices.
type Frontend struct {
	port            int
	pingClient      ping.PingServiceClient
	pongClient      pong.PongServiceClient
}

// NewFrontend creates a new Frontend instance with the specified configuration.
func NewFrontend(port int, pingaddr string, pongaddr string) *Frontend {
	f := &Frontend{
		port:            port,
		pingClient:      ping.NewPingServiceClient(dial(pingaddr)),
		pongClient:      pong.NewPongServiceClient(dial(pongaddr)),
	}
	return f
}

// Run starts the Frontend server and listens for incoming requests on the specified port.
func (s *Frontend) Run() error {
	http.Handle("/", http.FileServer(http.Dir("./static")))
	http.HandleFunc("/ping", s.pingHandler)
	http.HandleFunc("/ping-echo", s.pingEchoHandler)
	http.HandleFunc("/pong", s.pongHandler)
	http.HandleFunc("/pong-echo", s.pongEchoHandler)
	http.HandleFunc("/ping-pong", s.pingPongHandler)

	log.Printf("frontend server running at port: %d", s.port)
	return http.ListenAndServe(fmt.Sprintf(":%d", s.port), nil)
}

func (s *Frontend) pingHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	req := &ping.PingRequest{Body: "ping request"}
	reply, err := s.pingClient.Ping(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pingEchoHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	body := r.URL.Query().Get("body")
	log.Printf("pingEchoHandler get a request with body: %s", body)

	req := &ping.PingEchoRequest{Body: body}
	reply, err := s.pingClient.PingEcho(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pongHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	req := &pong.PongRequest{Body: "pong request"}
	reply, err := s.pongClient.Pong(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pongEchoHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	body := r.URL.Query().Get("body")
	log.Printf("pongEchoHandler get a request with body: %s", body)

	req := &pong.PongEchoRequest{Body: body}
	reply, err := s.pongClient.PongEcho(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pingPongHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	req := &ping.PingPongRequest{Body: "ping pong request"}
	reply, err := s.pingClient.PingPong(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

