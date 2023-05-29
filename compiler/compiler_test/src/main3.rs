use chrono::prelude::*;
use itertools::iproduct;

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
pub struct struct_acl {
    pub name: String,
    pub permission: String,
}

impl struct_acl {
    pub fn new(name: String, permission: String) -> struct_acl {
        struct_acl {
            name: name,
            permission: permission,
        }
    }
}
//TODO end of the code that needs to be generated

fn main() {
    let mut input: Vec<RpcMessage> = Vec::new();

    input.push(RpcMessage {
        event_type: "Type1".to_string(),
        source: "Banana".to_string(),
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
    let mut table_acl: Vec<struct_acl> = Vec::new();
    table_acl.push(struct_acl {
        permission: "Y".to_string(),
        name: "Banana".to_string(),
    });
    let output: Vec<_> = iproduct!(input.iter(), table_acl.iter())
        .filter(|&(input, acl)| input.source == acl.name && acl.permission == "Y")
        .map(|(l, _)| l.clone())
        .collect();
    // TODO end of code that needs to be generated

    println!("In OUTPUT:");
    for message in &output {
        println!(
            "Event Type: {}, Source: {}, Destination: {}, Payload: {}",
            message.event_type, message.source, message.destination, message.payload
        );
    }

    println!("ACL Test Pass!");
}
