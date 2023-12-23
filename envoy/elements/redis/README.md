# Redis

## Usage

```bash
# Deploy Redis
kubectl apply -f redis.yaml

# Test redis 
curl http://10.96.99.99:7379/PING # {"PING":[true,"PONG"]}

# Optional: insert and get an item
curl http://10.96.99.99:7379/SET/hello/world # {"SET":[true,"OK"]}
curl http://10.96.99.99:7379/GET/hello # {"GET":"world"}

# Apply the redis filter
kubectl apply -f redis-client.yaml

# Run curl and check the frontend proxy log
curl http://10.96.88.88:8080/ping-echo?body=redis
```

This element shows how to issue an HTTP call to a Redis service in Envoy. (Note: we are using https://github.com/nicolasff/webdis)

- Use `dispatch_http_call`` to initiate an asynchronous HTTP call to an external service.
- Implement `on_http_call_response`` to handle the incoming response (decode the result and act accordingly).
- Use `self.resume_http_request()` to resume the request/response processing.

Note: the filter configuration is different from other filters. Check `redis-client.yaml`.

Reference: https://github.com/proxy-wasm/proxy-wasm-rust-sdk/tree/master/examples/http_auth_random