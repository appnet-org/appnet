//! desired logging template
//! Requirements:
//! RpcMessage fields known, derived Clone.

#[derive(Clone, Debug)]
pub struct RpcMessage {
    pub event_type: String,
    pub source: String,
    pub destination: String,
    pub payload: String,
}

pub struct RPCEvent {
    pub event_type: String,
    pub source: String,
    pub destination: String,
    pub rpc: String,
}

impl RPCEvent {
    pub fn new(
        event_type: String,
        source: String,
        destination: String,
        payload: String,
    ) -> RPCEvent {
        RPCEvent {
            event_type: event_type,
            source: source,
            destination: destination,
            rpc: payload,
        }
    }
}

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

    let mut rpc_events: Vec<RPCEvent> = Vec::new();

    for event in input
        .iter()
        .map(|req| {
            RPCEvent::new(
                req.event_type.clone(),
                req.source.clone(),
                req.destination.clone(),
                req.payload.clone(),
            )
        })
        .collect::<Vec<_>>()
    {
        rpc_events.push(event);
    }

    let output: Vec<_> = input;

    println!("In RPC_EVENTS:");
    for message in &rpc_events {
        println!(
            "Event Type: {}, Source: {}, Destination: {}, Payload: {}",
            message.event_type, message.source, message.destination, message.rpc
        );
    }

    println!("In OUTPUT:");
    for message in &output {
        println!(
            "Event Type: {}, Source: {}, Destination: {}, Payload: {}",
            message.event_type, message.source, message.destination, message.payload
        );
    }

    // Following code should generate a compiler error:
    // error[E0382]: use of moved value: `input`
    // println!("Expected INPUT, consumed by OUTPUT {:?}", input);
}
