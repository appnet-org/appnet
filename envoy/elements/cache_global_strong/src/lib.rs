use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use serde_json::Value; 
use std::time::Duration;

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(CacheGlobalStrong { context_id })
    });
}

struct CacheGlobalStrong {
    #[allow(unused)]
    context_id: u32,
}

impl Context for CacheGlobalStrong {
    fn on_http_call_response(&mut self, _: u32, _: usize, body_size: usize, _: usize) {
        log::warn!("Got a response from Redis service.");
        if let Some(body) = self.get_http_call_response_body(0, body_size) {
            if let Ok(body_str) = std::str::from_utf8(&body) {
                log::warn!("Redis Response body: {}", body_str);
    
                // Parse the JSON response
                match serde_json::from_str::<Value>(body_str) {
                    Ok(json) => {
                        // Check if the GET field is not null
                        match json.get("GET") {
                            Some(get) if !get.is_null() => {
                                log::warn!("Cache hit!!!");
                                match get.as_str() {
                                    Some("cached") => {                                                                       
                                        // Run this code if the GET result is not null
                                        self.send_http_response(
                                            200,
                                            vec![
                                                ("grpc-status", "1"),
                                            ],
                                            None,
                                        );
                                    },
                                    Some(_) => log::warn!("Cache hit but not cached"),
                                    None => log::warn!("Cache hit but GET value is not a string"),
                                }
                                

                            },
                            _ => log::warn!("Cache miss!!!"),
                        }
                    },
                    Err(_) => log::warn!("Response body: [Invalid JSON data]"),
                }
            } else {
                log::warn!("Response body: [Non-UTF8 data]");
            }
            // I think this will be executed regardless of cache hit or miss
            self.resume_http_request();
        }
    }
}

impl HttpContext for CacheGlobalStrong {
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
                    log::warn!("Dispatching a call to redis service!");
                    let result = self.dispatch_http_call(
                        "webdis-service", // or your service name
                        vec![
                            (":method", "GET"),
                            (":path", &format!("/GET/{}", req.body)),
                            // (":path", "/GET/hello"),
                            (":authority", "webdis-service"), // Replace with the appropriate authority if needed
                        ],
                        None,
                        vec![],
                        Duration::from_secs(5),
                    )
                    .unwrap();
                    log::warn!("result: {}", result);
                    return Action::Pause;
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
        log::warn!("executing on_http_response_body");
        // if !end_of_stream {
        //     return Action::Pause;
        // }
        if let Some(body) = self.get_http_response_body(0, body_size) {
            // log::warn!("body: {:?}", body);
            // Parse grpc payload, skip the first 5 bytes
            match ping::PingEchoResponse::decode(&body[5..]) {
                Ok(req) => {
                    // Send an async request to redis to popular the cache.
                    // Xiangfeng: This really should be a synchronous request but I wasn't sure how to do it. 
                    log::warn!("Dispatching a call to Redis to save the response!");
                    let result = self.dispatch_http_call(
                        "webdis-service", // or your service name
                        vec![
                            (":method", "GET"),
                            (":path", &format!("/SET/{}/cached", req.body)),
                            // (":path", "/SET/redis/hello"),
                            (":authority", "webdis-service"), // Replace with the appropriate authority if needed
                        ],
                        None,
                        vec![],
                        Duration::from_secs(5),
                    )
                    .unwrap();
                    log::warn!("result: {}", result);
                    return Action::Pause
                }
                Err(e) => log::warn!("decode error: {}", e),
            }
        }
        Action::Continue
    }
}
