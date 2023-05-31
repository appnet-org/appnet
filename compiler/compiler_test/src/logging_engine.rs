use crate::engine::Engine;
use crate::engine::RpcMessage;
use chrono::prelude::*;

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

pub struct logging_engine {
    pub table_rpc_events: Vec<struct_rpc_events>,
}

impl Engine for logging_engine {
    fn init(&mut self) {
        self.table_rpc_events = Vec::new();
    }
    fn process(&mut self, input: Vec<RpcMessage>) -> Vec<RpcMessage> {
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
            self.table_rpc_events.push(event);
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

        output
    }
}
