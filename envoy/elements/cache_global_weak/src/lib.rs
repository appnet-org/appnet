use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use serde_json::Value; 
use proxy_wasm::traits::RootContext;
use std::time::Duration;
use std::collections::HashMap;
use lazy_static::lazy_static;
use std::sync::RwLock;

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

// A local cache 
lazy_static! {
    static ref REQUEST_CACHE: RwLock<HashMap<String, i32>> = RwLock::new(HashMap::new());
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_root_context(|_| -> Box<dyn RootContext> { Box::new(CacheGlobalWeakRoot) });
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(CacheGlobalWeak { context_id })
    });
}

struct CacheGlobalWeak {
    #[allow(unused)]
    context_id: u32,
}

struct CacheGlobalWeakRoot;

impl Context for CacheGlobalWeakRoot {}

impl RootContext for CacheGlobalWeakRoot {
    fn on_vm_start(&mut self, _: usize) -> bool {
        log::warn!("executing on_vm_start");
        self.set_tick_period(Duration::from_secs(5));
        true
    }

    fn on_tick(&mut self) {
        log::warn!("executing on_tick");
        // TODO(XZ): add logic to synchronize state here.
        self.dispatch_http_call(
            "webdis-service", // or your service name
            vec![
                (":method", "GET"),
                (":path", &format!("/SET/redis/cached")),
                // (":path", "/SET/redis/hello"),
                (":authority", "webdis-service"), // Replace with the appropriate authority if needed
            ],
            None,
            vec![],
            Duration::from_secs(5),
        )
        .unwrap();
    }
}

impl Context for CacheGlobalWeak {
    fn on_http_call_response(&mut self, _: u32, _: usize, body_size: usize, _: usize) {
        log::warn!("Got a response from Redis service.");
        if let Some(body) = self.get_http_call_response_body(0, body_size) {
            if let Ok(body_str) = std::str::from_utf8(&body) {
                log::warn!("Redis Response body: {}", body_str);
    
                // Parse the JSON response
                if let Ok(json) = serde_json::from_str::<Value>(body_str) {
                    // Check if the GET field is not null
                    if json.get("GET").is_some() && !json["GET"].is_null() {
                        log::warn!("Cache hit!!!");
                        // Run this code if the GET result is not null
                        self.send_http_response(
                            200,
                            vec![
                                ("grpc-status", "1"),
                            ],
                            None,
                        );
                    } else {
                        log::warn!("Cache miss!!!");
                    }
                } else {
                    log::warn!("Response body: [Invalid JSON data]");
                }
            } else {
                log::warn!("Response body: [Non-UTF8 data]");
            }
            // I think this will be executed regardless of cache hit or miss
            self.resume_http_request();
        }
    }
    
}

impl HttpContext for CacheGlobalWeak {
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
                    log::warn!("body : {}", req.body);
                    let map = REQUEST_CACHE.read().unwrap();

                    if map.contains_key(&req.body) {
                        log::warn!("Cache hit!!! body: {:?}", req.body);
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
                        log::warn!("Cache miss!!! body: {:?}", req.body);
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

    fn on_http_response_body(&mut self, body_size: usize, _end_of_stream: bool) -> Action {
        log::warn!("executing on_http_response_body!");
        // if !end_of_stream {
        //     return Action::Pause;
        // }
        if let Some(body) = self.get_http_response_body(0, body_size) {
            // log::warn!("body: {:?}", body);
            // Parse grpc payload, skip the first 5 bytes
            match ping::PingEchoResponse::decode(&body[5..]) {
                Ok(req) => {
                    log::warn!("Inserting request to local cache. Body : {}", req.body);
                    let mut map = REQUEST_CACHE.write().unwrap();
                    map.insert(req.body, 1);
                }
                Err(e) => log::warn!("decode error: {}", e),
            }
        }
        Action::Continue
   }
}
