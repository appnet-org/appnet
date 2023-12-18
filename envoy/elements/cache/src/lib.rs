use lazy_static::lazy_static;
use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use std::collections::HashMap;
use std::sync::Mutex;

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

lazy_static! {
    static ref REQUEST_BODIES: Mutex<HashMap<String, i32>> = Mutex::new(HashMap::new());
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Cache { context_id })
    });
}

struct Cache {
    #[allow(unused)]
    context_id: u32,
}

impl Context for Cache {}

impl HttpContext for Cache {
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

        // Replace the message body if it contains the text "secret".
        // Since we returned "Pause" previuously, this will return the whole body.
        if let Some(body) = self.get_http_request_body(0, body_size) {
            // log::warn!("body: {:?}", body);
            // Parse grpc payload, skip the first 5 bytes
            match ping::PingEchoRequest::decode(&body[5..]) {
                Ok(req) => {
                    // log::info!("req: {:?}", req);
                    // log::warn!("body.len(): {}", req.body.len());
                    // log::warn!("body : {}", req.body);
                    let mut map = REQUEST_BODIES.lock().unwrap();

                    if map.contains_key(&req.body) {
                        self.send_http_response(
                            200,
                            vec![
                                ("grpc-status", "1"),
                                // ("grpc-message", "Access forbidden.\n"),
                            ],
                            None,
                        );
                        return Action::Pause;
                    } else {
                        return Action::Continue;
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

    fn on_http_response_body(&mut self, body_size: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_response_body");
        if !end_of_stream {
            return Action::Pause;
        }
        if let Some(body) = self.get_http_request_body(0, body_size) {
            // log::warn!("body: {:?}", body);
            // Parse grpc payload, skip the first 5 bytes
            match ping::PingEchoRequest::decode(&body[5..]) {
                Ok(req) => {
                    // log::info!("req: {:?}", req);
                    // log::warn!("body.len(): {}", req.body.len());
                    // log::warn!("body : {}", req.body);
                    let mut map = REQUEST_BODIES.lock().unwrap();
                    map.insert(req.body, 1);
                }
                Err(e) => log::warn!("decode error: {}", e),
            }
        }
        Action::Continue
    }
}
