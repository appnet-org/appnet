# Random Authorization

This element shows how to issue an external HTTP call in Envoy.

- Use `dispatch_http_call`` to initiate an asynchronous HTTP call to an external service.
- Implement `on_http_call_response`` to handle the incoming response (decode the result and act accordingly).
- Use `self.resume_http_request()` to resume the request/response processing.

Note: the filter configuration is different from other filters. Check `auth-client.yaml`.

Reference: https://github.com/proxy-wasm/proxy-wasm-rust-sdk/tree/master/examples/http_auth_random