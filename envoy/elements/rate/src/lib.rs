use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::cmp;
// use std::sync::Mutex;
// use std::time::{SystemTime, UNIX_EPOCH};

// use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

static TOKEN: AtomicUsize = AtomicUsize::new(100);
// lazy_static! {
//     static ref LAST_TIMESTAMP: Mutex<u64> = Mutex::new(SystemTime::now()
//         .duration_since(UNIX_EPOCH)
//         .expect("Time went backwards")
//         .as_secs());
// }

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Ratelimit { context_id, last_ts: self.get_current_time().into().timestamp() as f64, limit : 100, per_sec: 1 })
    });
}

struct Ratelimit {
    #[allow(unused)]
    context_id: u32,
    last_ts: f64,
    limit: u32,
    per_sec: u32,
}

impl Context for Ratelimit {}

impl HttpContext for Ratelimit {
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
        
        // TODO: Add logic to caculate the current timestamp
        self.num_tokens = cmp::min(self.limit, self.num_tokens
        + (self.get_current_time().into().timestamp() as f64 - self.last_ts)
            * self.per_sec as f64);
        self.last_ts = self.get_current_time().into().timestamp() as f64;


        if curr_token < 1 {
            self.send_http_response(
                200,
                vec![
                    ("grpc-status", "1"),
                    // ("grpc-message", "Access forbidden.\n"),
                ],
                None,
            );
            return Action::Pause;
        }

        Action::Continue
    }

    fn on_http_response_headers(&mut self, _num_headers: usize, _end_of_stream: bool) -> Action {
        log::warn!("executing on_http_response_headers");

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
