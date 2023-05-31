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

pub trait Engine {
    fn process(&mut self, input: Vec<RpcMessage>) -> Vec<RpcMessage>;
    fn init(&mut self);
}
