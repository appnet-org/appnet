use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use proxy_wasm::traits::RootContext;
use lazy_static::lazy_static;
use std::collections::HashMap;
use std::sync::Mutex;

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

lazy_static! {
    static ref LB_TABLE: Mutex<HashMap<String, i32>> = Mutex::new(HashMap::new());
}


#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_root_context(|_| -> Box<dyn RootContext> { Box::new(LoadBalanceRoot) });
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(LoadBalanceBody { context_id })
    });
}

struct LoadBalanceRoot;

impl Context for LoadBalanceRoot {}

impl RootContext for LoadBalanceRoot {
    fn on_vm_start(&mut self, _: usize) -> bool {
        log::warn!("executing on_vm_start");
        true
    }
}

struct LoadBalanceBody {
    #[allow(unused)]
    context_id: u32,
}

impl Context for LoadBalanceBody {}

impl HttpContext for LoadBalanceBody {
    fn on_http_request_headers(&mut self, _num_of_headers: usize, end_of_stream: bool) -> Action {
        log::warn!("executing on_http_request_headers");
        if !end_of_stream {
            return Action::Continue;
        }

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
                    let mut map = LB_TABLE.lock().unwrap();
                    
                    if map.contains_key(&req.body) {
                        log::warn!("LB Table hit!!");
                        // self.set_http_request_header("destination", None);
                    } else {
                        // log::warn!("executing on_http_request_body");
                        log::warn!("LB Table miss!!");
                        // self.set_http_request_header("destination", None);
                        map.insert(req.body, 1);
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
