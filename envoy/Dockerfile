FROM golang:1.18-alpine as builder
# Set the working directory inside the container
WORKDIR /app
# Copy only the necessary Go mod files to cache dependencies
COPY go.mod go.sum ./
# Download and cache Go dependencies
RUN go mod download
# Copy the entire project directory to the container
COPY . .
# Build the Go application with optimized flags
RUN go build -ldflags="-s -w" -o /app/ping-pong ./cmd/...
# Use a minimal base image for the final container
FROM alpine:latest
# Set the working directory inside the container
WORKDIR /app
# Copy the built binary from the builder stage
COPY --from=builder /app/ping-pong .
# Set the entrypoint command to run the binary
CMD ["./ping-pong"]