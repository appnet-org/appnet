use crate::engine::Engine;
use crate::engine::RpcMessage;
use chrono::prelude::*;
use itertools::iproduct;

pub struct fault_engine {}

impl Engine for fault_engine {
    fn init(&mut self) {}
    fn process(&mut self, input: Vec<RpcMessage>) -> Vec<RpcMessage> {
        let var_probability = 0.2;
        let output: Vec<_> = input
            .iter()
            .filter(|&item| rand::random::<f32>() < var_probability)
            .cloned()
            .collect();

        output
    }
}
