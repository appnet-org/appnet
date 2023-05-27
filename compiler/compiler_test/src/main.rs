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

    for message in &input {
        println!("Event Type: {}, Source: {}, Destination: {}, Payload: {}", message.event_type, message.source, message.destination, message.payload);
    }

    let rpc_events: Vec<RPCEvent> = Vec::new();

    for event in input.iter().map(|req| RPCEvent::new(req.event_type, req.source, req.destination, req.payload)).collect::<Vec<_>>() { rpc_events.push(event); }
}
