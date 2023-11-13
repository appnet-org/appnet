package services

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/UWNetworksLab/app-defined-networks/envoy/ping_pb"
	"github.com/UWNetworksLab/app-defined-networks/envoy/pong_pb"
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

	req := &ping.PingRequest{body: "ping request"}
	reply, err := s.pingClient.ping(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pingHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()


	req := &ping.PingRequest{body: "ping request"}
	reply, err := s.pingClient.ping(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pingEchoHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	body := r.URL.Query().Get("body")

	req := &ping.PingEchoRequest{body: body}
	reply, err := s.pingClient.pingEcho(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pongHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	req := &pong.PongRequest{body: "pong request"}
	reply, err := s.pongClient.pong(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pongEchoHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	body := r.URL.Query().Get("body")

	req := &pong.PongEchoRequest{body: body}
	reply, err := s.pongClient.pongEcho(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

func (s *Frontend) pingPongHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	req := &ping.PingRequest{body: "ping pong request"}
	reply, err := s.pingClient.pingPong(ctx, req)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(reply)
}

