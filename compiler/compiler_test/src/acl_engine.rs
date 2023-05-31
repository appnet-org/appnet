use crate::engine::Engine;
use crate::engine::RpcMessage;
use chrono::prelude::*;
use itertools::iproduct;

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

pub struct acl_engine {
    pub table_acl: Vec<struct_acl>,
}

impl Engine for acl_engine {
    fn init(&mut self) {
        self.table_acl = Vec::new();
    }
    fn process(&mut self, input: Vec<RpcMessage>) -> Vec<RpcMessage> {
        self.table_acl.push(struct_acl {
            permission: "Y".to_string(),
            name: "Banana".to_string(),
        });
        let output: Vec<_> = iproduct!(input.iter(), self.table_acl.iter())
            .filter(|&(input, acl)| input.source == acl.name && acl.permission == "Y")
            .map(|(l, _)| l.clone())
            .collect();

        output
    }
}
