use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use proxy_wasm::traits::RootContext;
use std::sync::atomic::{AtomicUsize, Ordering};
// use std::cmp;
use std::sync::Mutex;
use lazy_static::lazy_static;
// use std::time::{SystemTime, UNIX_EPOCH};

// use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

static TOKEN: AtomicUsize = AtomicUsize::new(1);
lazy_static! {
    static ref LAST_TS: Mutex<f64> = Mutex::new(0.0);
}


#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Ratelimit { context_id, limit : 100, per_sec: 1 })
    });
}

struct Ratelimit {
    #[allow(unused)]
    context_id: u32,
    limit: u32,
    per_sec: u32,
}

impl Context for Ratelimit {}

impl RootContext for Ratelimit {
    fn on_configure(&mut self, _: usize) -> bool {
        let mut last_ts = LAST_TS.lock().unwrap();
        *last_ts = self.get_current_time().into().timestamp() as f64;
        true
    }
}

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
        let mut last_ts = LAST_TS.lock().unwrap();
        let token_to_add = ((self.get_current_time().into().timestamp() as f64 - *last_ts) * self.per_sec as f64).floor() as usize;
        log::warn!("Current token value: {}", token_to_add);
        TOKEN.fetch_add(token_to_add, Ordering::SeqCst)
        *last_ts = self.get_current_time().into().timestamp() as f64;


        if TOKEN.load(Ordering::SeqCst) >= 1 {
            TOKEN.fetch_sub(1, Ordering::SeqCst);
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
