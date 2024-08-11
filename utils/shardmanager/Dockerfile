FROM golang:1.22.1-bullseye AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o main .

FROM alpine:latest
COPY --from=builder /app/main /main

# Command to run the executable
CMD ["./main"]
