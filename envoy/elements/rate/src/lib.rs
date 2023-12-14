use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use proxy_wasm::traits::RootContext;
use std::sync::atomic::{AtomicUsize, Ordering};
use chrono::{DateTime, Utc};
use std::sync::Mutex;
use lazy_static::lazy_static;


// use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

static TOKEN: AtomicUsize = AtomicUsize::new(0);
lazy_static! {
    static ref LAST_TS: Mutex<f64> = Mutex::new(0.0);
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_root_context(|_| -> Box<dyn RootContext> { Box::new(RatelimitRoot) });
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(RatelimitBody { context_id, limit : 100, per_sec: 0.1 })
    });
}

struct RatelimitRoot;

impl Context for RatelimitRoot {}

impl RootContext for RatelimitRoot {
    fn on_vm_start(&mut self, _: usize) -> bool {
        log::warn!("executing on_vm_start");
        let mut last_ts = LAST_TS.lock().unwrap();
        let now: DateTime<Utc> = self.get_current_time().into();
        *last_ts = now.timestamp() as f64;
        log::warn!("Current timestamp is: {}", last_ts);
        true
    }
}

struct RatelimitBody {
    #[allow(unused)]
    context_id: u32,
    limit: u32,
    per_sec: f32,
}

impl Context for RatelimitBody {}

impl HttpContext for RatelimitBody {
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
        
        let now: DateTime<Utc> = self.get_current_time().into();
        let mut last_ts = LAST_TS.lock().unwrap();
        let token_to_add = ((now.timestamp() as f64 - *last_ts) * self.per_sec as f64).floor() as usize;
        log::warn!("token_to_add is: {}", token_to_add);
        log::warn!("token_to_add+current_token is: {}", token_to_add+TOKEN.load(Ordering::SeqCst));
        let token_to_store = std::cmp::min(token_to_add+TOKEN.load(Ordering::SeqCst), self.limit.try_into().unwrap());
        log::warn!("token_to_store is: {}", token_to_store);
        TOKEN.store(token_to_store, Ordering::SeqCst);
        *last_ts = now.timestamp() as f64;
        log::warn!("Current token is: {}", TOKEN.load(Ordering::SeqCst));



        if TOKEN.load(Ordering::SeqCst) < 1 {
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

        TOKEN.fetch_sub(1, Ordering::SeqCst);

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
