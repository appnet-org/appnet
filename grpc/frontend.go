package main

import (
	"fmt"
	"log"
	"net/http"

	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"

	// "github.com/UWNetworksLab/adn-controller/grpc/interceptors/null"

	echo "github.com/UWNetworksLab/adn-controller/grpc/pb"
)

func handler(writer http.ResponseWriter, request *http.Request) {
	// requestBody := strings.Replace(request.URL.String(), "/", "", -1)
	requestBody := request.URL.Query().Get("key")
	fmt.Printf("Got request with key: %s\n", requestBody)

	var conn *grpc.ClientConn

	conn, err := grpc.Dial(
		"server:9000",
		grpc.WithInsecure(),
	)
	if err != nil {
		log.Fatalf("could not connect: %s", err)
	}
	defer conn.Close()

	c := echo.NewEchoServiceClient(conn)

	// Create and attach metadata with the custom header
	md := metadata.New(map[string]string{
		"key": requestBody, // Here we're setting the custom header "key" to the requestBody
	})
	ctx := metadata.NewOutgoingContext(context.Background(), md)

	message := echo.Msg{
		Body: requestBody,
	}

	// Make sure to pass the context (ctx) which includes the metadata
	response, err := c.Echo(ctx, &message)
	if err != nil {
		fmt.Fprintf(writer, "Echo server returns an error.\n")
		log.Printf("Error when calling echo: %s", err)
	} else {
		fmt.Fprintf(writer, "%s", response.Body)
		log.Printf("Response from server: %s", response.Body)
	}
}

func main() {
	http.HandleFunc("/", handler)

	fmt.Printf("Starting frontend pod at port 8080\n")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
