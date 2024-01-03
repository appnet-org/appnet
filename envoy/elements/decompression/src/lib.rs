use proxy_wasm::traits::{Context, HttpContext};
use proxy_wasm::types::{Action, LogLevel};
use flate2::{read::GzDecoder};
use std::io::{Read};
use base64::{engine::general_purpose, Engine as _};

use prost::Message;
pub mod ping {
    include!(concat!(env!("OUT_DIR"), "/ping_pb.rs"));
}

#[no_mangle]
pub fn _start() {
    proxy_wasm::set_log_level(LogLevel::Trace);
    proxy_wasm::set_http_context(|context_id, _| -> Box<dyn HttpContext> {
        Box::new(Decompression { context_id })
    });
}

struct Decompression {
    #[allow(unused)]
    context_id: u32,
}

impl Context for Decompression {}

impl HttpContext for Decompression {
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
            log::warn!("Body size: {}", body.len());
            log::warn!("body: {:?}", body);
            if body.len() > 5 {
                // The gRPC message may be changed/compressed - better use the new length. 
                // This step is required as the body_size will be inaccurate.
                let message_length = u32::from_be_bytes([body[1], body[2], body[3], body[4]]) as usize + 5;
                log::warn!("gRPC message length: {}", message_length);
                if let Ok(mut req) = ping::PingEchoRequest::decode(&body[5..message_length]) {
                    // Decompress and re-encode
                    
                    let decoded_data = general_purpose::STANDARD.decode(&req.body).expect("Failed to decode Base64 string");
                    let mut decoder = GzDecoder::new(&decoded_data[..]);
                    let mut decompressed_data = String::new();
                    decoder.read_to_string(&mut decompressed_data).unwrap();

                    req.body = decompressed_data;
                    let mut new_body = Vec::new();
                    req.encode(&mut new_body).expect("Failed to encode");

                    // Construct the gRPC header
                    let new_body_length = new_body.len() as u32;
                    let mut grpc_header = Vec::new();
                    grpc_header.push(0); // Compression flag
                    grpc_header.extend_from_slice(&new_body_length.to_be_bytes());

                    // log::warn!("Header size: {}", grpc_header.len());

                    // Combine header and body
                    grpc_header.append(&mut new_body);

                    // Replace the request body
                    self.set_http_request_body(0, grpc_header.len(), &grpc_header);
                } else {
                    log::warn!("Failed to decode the request body");
                }
            } else {
                log::warn!("Received body is too short to be a valid gRPC message");
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
