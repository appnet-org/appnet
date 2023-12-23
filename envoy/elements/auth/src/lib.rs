use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

static GLOBAL_COUNTER: AtomicUsize = AtomicUsize::new(0);

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(AuthRandom { context_id })
    });
}

struct AuthRandom {
    #[allow(unused)]
    context_id: u32,
}

impl Context for AuthRandom {
    fn on_http_call_response(&mut self, _: u32, _: usize, body_size: usize, _: usize) {
        log::warn!("Got a response.");
        if let Some(body) = self.get_http_call_response_body(0, body_size) {
            if !body.is_empty() && body[0] % 2 == 0 {
                log::warn!("Access granted.");
                self.resume_http_request();
                return;
            }
        }
        log::warn!("Access forbidden.");

        let counter_val = GLOBAL_COUNTER.fetch_add(1, Ordering::SeqCst) + 1;
        log::warn!("Global counter value: {}", counter_val);
        self.send_http_response(
            403,
            vec![
                ("grpc-status", "7"),
            ],
            None,
        );
    }
}

impl HttpContext for AuthRandom {
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
                    if req.body == "auth" {
                        log::warn!("Dispatching a call to httpbin");
                        self.dispatch_http_call(
                            "httpbin",
                            vec![
                                (":method", "GET"),
                                (":path", "/bytes/1"),
                                (":authority", "httpbin.org"),
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



