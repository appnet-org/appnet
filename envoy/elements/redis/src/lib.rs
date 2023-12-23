use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
// use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Redis { context_id })
    });
}

struct Redis {
    #[allow(unused)]
    context_id: u32,
}

impl Context for Redis {
    fn on_http_call_response(&mut self, _: u32, _: usize, body_size: usize, _: usize) {
        log::warn!("Got a response from Redis service.");
        if let Some(body) = self.get_http_call_response_body(0, body_size) {
            if let Ok(body_str) = std::str::from_utf8(&body) {
                log::warn!("Response body: {}", body_str);
            } else {
                log::warn!("Response body: [Non-UTF8 data]");
            }
            self.resume_http_request();
        }
    }
}

impl HttpContext for Redis {
    fn on_http_request_headers(&mut self, _num_of_headers: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_request_headers");
        if !end_of_stream {
            return Action::Continue;
        }

        self.set_http_response_header("content-length", None);
        Action::Continue
    }

    fn on_http_request_body(&mut self, body_size: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_request_body");
        if !end_of_stream {
            return Action::Pause;
        }

        if let Some(body) = self.get_http_request_body(0, body_size) {
            match ping::PingEchoRequest::decode(&body[5..]) {
                Ok(req) => {
                    if req.body == "redis" {
                        log::warn!("Dispatching a call to redis");
                        self.dispatch_http_call(
                            "webdis-service", // or your service name
                            vec![
                                (":method", "GET"),
                                (":path", "/GET/hello"),
                                (":authority", "webdis-service"), // Replace with the appropriate authority if needed
                            ],
                            None,
                            vec![],
                            Duration::from_secs(5),
                        )
                        .unwrap();
                        return Action::Pause;
                    }
                }
                Err(e) => log::warn!("decode error: {}", e),
            }
        }

        Action::Continue
    }

    fn on_http_response_headers(&mut self, _num_headers: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_response_headers");
        if !end_of_stream {
            return Action::Continue;
        }

        Action::Continue
    }

    fn on_http_response_body(&mut self, _body_size: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_response_body");
        if !end_of_stream {
            return Action::Pause;
        }

        Action::Continue
    }
}



