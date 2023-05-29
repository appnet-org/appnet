use chrono::prelude::*;
use itertools::iproduct;
use rand;
#[derive(Clone, Debug)]
pub struct RpcMessage {
    pub event_type: String,
    pub source: String,
    pub destination: String,
    pub payload: String,
}

impl RpcMessage {
    pub fn new(
        event_type: String,
        source: String,
        destination: String,
        payload: String,
    ) -> RpcMessage {
        RpcMessage {
            event_type: event_type,
            source: source,
            destination: destination,
            payload: payload,
        }
    }
}

// TODO start of the code that needs to be generated
//TODO end of the code that needs to be generated

fn main() {
    let mut input: Vec<RpcMessage> = Vec::new();

    for i in 1..100 {
        input.push(RpcMessage {
            event_type: "Type1".to_string(),
            source: "Source1".to_string(),
            destination: "Destination1".to_string(),
            payload: "Payload1".to_string(),
        });
    }

    println!("input size = {}", input.len());

    // TODO start of the code that needs to be generated
    let var_probability = 0.2;
    let output: Vec<_> = input
        .iter()
        .filter(|&item| rand::random::<f32>() < var_probability)
        .cloned()
        .collect();

    // TODO end of code that needs to be generated

    println!("output size = {}", output.len());

    println!("Fault Test Pass!");
}
