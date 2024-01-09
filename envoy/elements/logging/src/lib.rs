use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Logging { context_id, method: "".to_string()})
    });
}

struct Logging {
    #[allow(unused)]
    context_id: u32,
    method: String,
}

impl Context for Logging {}

impl HttpContext for Logging {
    fn on_http_request_headers(&mut self, num_of_headers: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_request_headers!!!");
        // log::warn!("Got {} HTTP headers in #{}.", num_of_headers, self.context_id);
        // if !end_of_stream {
        //     return Action::Continue;
        // }

        
        // for (name, value) in &self.get_http_request_headers() {
        //     log::warn!("#{} -> {}: {}", self.context_id, name, value);
        // }

        match self.get_http_request_header(":path") {
            Some(path)  => {
                self.method = path.rsplit('/').next().unwrap_or("").to_string();
            }
            _ => log::warn!("No path header found!"), 
        }

        self.set_http_request_header("content-length", None);
        Action::Continue
    }

    fn on_http_request_body(&mut self, body_size: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_request_body");
        log::warn!("Context id #{} and path is {}.", self.context_id, self.method);
        // if !end_of_stream {
        //     return Action::Pause;
        // }

        // Replace the message body if it contains the text "secret".
        // Since we returned "Pause" previuously, this will return the whole body.
        if let Some(body) = self.get_http_request_body(0, body_size) {
            // log::warn!("body: {:?}", body);
            // Parse grpc payload, skip the first 5 bytes
            match ping::PingEchoRequest::decode(&body[5..]) {
                Ok(req) => {
                    log::warn!("body.len(): {}", req.body.len());
                    log::warn!("body : {}", req.body);
                }
                Err(e) => log::warn!("decode error: {}", e),
            }
        }

        Action::Continue
    }

    fn on_http_response_headers(&mut self, _num_headers: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_response_headers");
        // if !end_of_stream {
        //     return Action::Continue;
        // }

        // for (name, value) in &self.get_http_response_headers() {
        //     log::warn!("#{} -> {}: {}", self.context_id, name, value);
        // }

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
