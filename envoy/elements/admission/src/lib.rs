use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use std::sync::atomic::{AtomicUsize, Ordering};
use rand::Rng;

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
        Box::new(AdmissionControl { context_id, multiplier : 0.5 })
    });
}

struct AdmissionControl {
    #[allow(unused)]
    context_id: u32,
    multiplier: f32,
}

impl Context for AdmissionControl {}

impl HttpContext for AdmissionControl {
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
        let total = SEND_COUNT.fetch_add(1, Ordering::SeqCst) + 1;

        // Caculate client request rejection probability
        let acc_prob = (total as f32 - self.multiplier * (SUCCESS_COUNT.load(Ordering::SeqCst) as f32)) / ((total + 1) as f32);
        log::warn!("Accept probability: {}", acc_prob);

        let mut rng = rand::thread_rng();
        let rand_num = rng.gen_range(0.0, 1.0);

        if rand_num > acc_prob {
            self.send_http_response(
                403,
                vec![
                    ("grpc-status", "1"),
                ],
                None,
            );
        }

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
