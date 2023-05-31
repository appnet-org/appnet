mod acl_engine;
mod engine;
mod fault_engine;
mod logging_engine;
use chrono::prelude::*;
use engine::Engine;
use engine::RpcMessage;
fn prepare() -> Vec<RpcMessage> {
    let mut input: Vec<RpcMessage> = Vec::new();

    for i in 1..10 {
        input.push(RpcMessage {
            event_type: "Type1".to_string(),
            source: "Banana".to_string(),
            destination: "Destination1".to_string(),
            payload: "Payload1".to_string(),
        });
        input.push(RpcMessage {
            event_type: "Type2".to_string(),
            source: "Banana".to_string(),
            destination: "Destination2".to_string(),
            payload: "Payload2".to_string(),
        });
    }
    for i in 1..10 {
        input.push(RpcMessage {
            event_type: "Type0".to_string(),
            source: "Apple".to_string(),
            destination: "Destination0".to_string(),
            payload: "Payload0".to_string(),
        });
    }

    input
}

fn describe(input: &Vec<RpcMessage>) {
    println!("input size = {}", input.len());
    for i in 0..input.len() {
        println!("input[{}] = {:?}", i, input[i]);
    }
}

fn main() {
    let mut input: Vec<RpcMessage> = prepare();

    let mut fault_engine = fault_engine::fault_engine {};
    fault_engine.init();

    let mut log_engine = logging_engine::logging_engine {
        table_rpc_events: Vec::new(),
    };
    log_engine.init();

    let mut acl_engine = acl_engine::acl_engine {
        table_acl: Vec::new(),
    };
    acl_engine.init();

    input = fault_engine.process(input);
    describe(&input);

    input = log_engine.process(input);
    describe(&input);

    input = acl_engine.process(input);
    describe(&input);

    println!("Finish!");
}
