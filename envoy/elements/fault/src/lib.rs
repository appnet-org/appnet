use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use rand::Rng;

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Fault { context_id, abort_probability : 0.5 })
    });
}

struct Fault {
    #[allow(unused)]
    context_id: u32,
    abort_probability: f32
}

impl Context for Fault {}

impl HttpContext for Fault {
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
            // log::warn!("body: {:?}", body);
            // Parse grpc payload, skip the first 5 bytes
            match ping::PingEchoRequest::decode(&body[5..]) {
                Ok(req) => {
                    // log::warn!("req: {:?}", req);
                    // log::warn!("body.len(): {}", req.body.len());
                    // log::warn!("body : {}", req.body);
                    if req.body == "fault" {
                        // Status code: https://chromium.googlesource.com/external/github.com/grpc/grpc/+/refs/tags/v1.21.4-pre1/doc/statuscodes.md

                        let mut rng = rand::thread_rng();
                        // let rand_num = rng.gen_range(0.0..1.0); // Generate a random number between 0 and 1
                        let rand_num = rng.gen_range(0.0, 1.0); // Generate a random number between 0 and 1

                        // log::warn!("Generated random number: {}", rand_num);

                        if rand_num < self.abort_probability {
                            // log::warn!("Generated random number: {}", rand_num);
                            self.send_http_response(
                                // 200,
                                200, // 403 
                                vec![
                                    ("grpc-status", "1"), // 1 = CANCELLED
                                    // ("grpc-message", "Access forbidden.\n"),
                                ],
                                None,
                            );
                        }
                    // return Action::Pause;
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