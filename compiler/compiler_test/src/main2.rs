use chrono::prelude::*;

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
pub struct struct_rpc_events {
    pub timestamp: DateTime<Utc>,
    pub event_type: String,
    pub source: String,
    pub destination: String,
    pub rpc: String,
}

impl struct_rpc_events {
    pub fn new(
        timestamp: DateTime<Utc>,
        event_type: String,
        source: String,
        destination: String,
        rpc: String,
    ) -> struct_rpc_events {
        struct_rpc_events {
            timestamp: timestamp,
            event_type: event_type,
            source: source,
            destination: destination,
            rpc: rpc,
        }
    }
}
//TODO end of the code that needs to be generated

fn main() {
    let mut input: Vec<RpcMessage> = Vec::new();

    input.push(RpcMessage {
        event_type: "Type1".to_string(),
        source: "Source1".to_string(),
        destination: "Destination1".to_string(),
        payload: "Payload1".to_string(),
    });

    input.push(RpcMessage {
        event_type: "Type2".to_string(),
        source: "Source2".to_string(),
        destination: "Destination2".to_string(),
        payload: "Payload2".to_string(),
    });

    println!("In INPUT:");
    for message in &input {
        println!(
            "Event Type: {}, Source: {}, Destination: {}, Payload: {}",
            message.event_type, message.source, message.destination, message.payload
        );
    }

    // TODO start of the code that needs to be generated
    let mut table_rpc_events: Vec<struct_rpc_events> = Vec::new();
    for event in input
        .iter()
        .map(|req| {
            struct_rpc_events::new(
                Utc::now(),
                req.event_type.clone(),
                req.source.clone(),
                req.destination.clone(),
                req.payload.clone(),
            )
        })
        .collect::<Vec<_>>()
    {
        table_rpc_events.push(event);
    }
    let output: Vec<_> = input
        .iter()
        .map(|req| {
            RpcMessage::new(
                req.event_type.clone(),
                req.source.clone(),
                req.destination.clone(),
                req.payload.clone(),
            )
        })
        .collect::<Vec<_>>();
    // TODO end of code that needs to be generated

    println!("In OUTPUT:");
    for message in &output {
        println!(
            "Event Type: {}, Source: {}, Destination: {}, Payload: {}",
            message.event_type, message.source, message.destination, message.payload
        );
    }

    println!("Logging Test Pass!");
}
