use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use std::sync::atomic::{AtomicUsize, Ordering};

// use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

static SEND_COUNT: AtomicUsize = AtomicUsize::new(0);
static SUCCESS_COUNT: AtomicUsize = AtomicUsize::new(0);


#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Metrics { context_id })
    });
}

struct Metrics {
    #[allow(unused)]
    context_id: u32,
}

impl Context for Metrics {}

impl HttpContext for Metrics {
    fn on_http_request_headers(&mut self, _num_of_headers: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_request_headers");
        if !end_of_stream {
            return Action::Continue;
        }

        self.set_http_response_header("content-length", None);
        Action::Continue
    }

    fn on_http_request_body(&mut self, _body_size: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_request_body");
        if !end_of_stream {
            return Action::Pause;
        }

        let _ = SEND_COUNT.fetch_add(1, Ordering::SeqCst) + 1;

        Action::Continue
    }

    fn on_http_response_headers(&mut self, _num_headers: usize, _end_of_stream: bool) -> Action {
        log::warn!("executing on_http_response_headers");

        // Check the response headers
        if let Some(status_code) = self.get_http_response_header(":status") {
            if status_code == "200" {
                // Print a message if the status code is 200
                // log::warn!("Status code is 200 - Success");

                let _ = SUCCESS_COUNT.fetch_add(1, Ordering::SeqCst) + 1;
            }
        } else {
            log::warn!("No status code found in response headers");
        }

        log::warn!("Request Sent: {}", SEND_COUNT.load(Ordering::SeqCst));
        log::warn!("Response Received: {}", SUCCESS_COUNT.load(Ordering::SeqCst));

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
