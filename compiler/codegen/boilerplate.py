include = r"""
use chrono::prelude::*;
use itertools::iproduct;
use rand::Rng;
use minstant::Instant;

"""

config_rs = """
use chrono::{{Datelike, Timelike, Utc}};
use phoenix_common::log;
use serde::{{Deserialize, Serialize}};
{Include}
{GlobalFunctionInclude}
{InternalStatesDeclaration}


#[derive(Debug, Clone, Copy, Default, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct {TemplateNameFirstCap}Config {{}}


impl {TemplateNameFirstCap}Config {{
    /// Get config from toml file
    pub fn new(config: Option<&str>) -> anyhow::Result<Self> {{
        let config = toml::from_str(config.unwrap_or(""))?;
        Ok(config)
    }}
}}


pub fn create_log_file() -> std::fs::File {{
    std::fs::create_dir_all("/tmp/phoenix/log").expect("mkdir failed");
    let now = Utc::now();
    let date_string = format!(
        "{{}}-{{}}-{{}}-{{}}-{{}}-{{}}",
        now.year(),
        now.month(),
        now.day(),
        now.hour(),
        now.minute(),
        now.second()
    );
    let file_name = format!("/tmp/phoenix/log/logging_engine_{{}}.log", date_string);
    ///log::info!("create log file {{}}", file_name);
    let log_file = std::fs::File::create(file_name).expect("create file failed");
    log_file
}}

"""

lib_rs = """
#![feature(peer_credentials_unix_socket)]
#![feature(ptr_internals)]
#![feature(strict_provenance)]
use thiserror::Error;

{InternalStatesDeclaration}
{Include}

pub use phoenix_common::{{InitFnResult, PhoenixAddon}};

pub mod config;
pub(crate) mod engine;
pub mod module;

#[derive(Error, Debug)]
pub(crate) enum DatapathError {{
    #[error("Internal queue send error")]
    InternalQueueSend,
}}

use phoenix_common::engine::datapath::SendError;
impl<T> From<SendError<T>> for DatapathError {{
    fn from(_other: SendError<T>) -> Self {{
        DatapathError::InternalQueueSend
    }}
}}

use crate::config::{TemplateNameFirstCap}Config;
use crate::module::{TemplateNameFirstCap}Addon;

#[no_mangle]
pub fn init_addon(config_string: Option<&str>) -> InitFnResult<Box<dyn PhoenixAddon>> {{
    let config = {TemplateNameFirstCap}Config::new(config_string)?;
    let addon = {TemplateNameFirstCap}Addon::new(config);
    Ok(Box::new(addon))
}}
"""

module_rs = """
use anyhow::{{bail, Result}};
use nix::unistd::Pid;

use phoenix_common::addon::{{PhoenixAddon, Version}};
use phoenix_common::engine::datapath::DataPathNode;
use phoenix_common::engine::{{Engine, EngineType}};
use phoenix_common::storage::ResourceCollection;

use super::engine::{TemplateNameFirstCap}Engine;
use crate::config::{{create_log_file, {TemplateNameFirstCap}Config}};
{InternalStatesDeclaration}
{Include}
{GlobalFunctionInclude}

pub(crate) struct {TemplateNameFirstCap}EngineBuilder {{
    node: DataPathNode,
    config: {TemplateNameFirstCap}Config,
}}

impl {TemplateNameFirstCap}EngineBuilder {{
    fn new(node: DataPathNode, config: {TemplateNameFirstCap}Config) -> Self {{
        {TemplateNameFirstCap}EngineBuilder {{ node, config }}
    }}
    // TODO! LogFile
    fn build(self) -> Result<{TemplateNameFirstCap}Engine> {{
        {InternalStatesOnBuild}
        Ok({TemplateNameFirstCap}Engine {{
            node: self.node,
            indicator: Default::default(),
            config: self.config,
            {InternalStatesInConstructor}
        }})
    }}
}}

pub struct {TemplateNameFirstCap}Addon {{
    config: {TemplateNameFirstCap}Config,
}}

impl {TemplateNameFirstCap}Addon {{
    pub const {TemplateNameAllCap}_ENGINE: EngineType = EngineType("{TemplateNameFirstCap}Engine");
    pub const ENGINES: &'static [EngineType] = &[{TemplateNameFirstCap}Addon::{TemplateNameAllCap}_ENGINE];
}}

impl {TemplateNameFirstCap}Addon {{
    pub fn new(config: {TemplateNameFirstCap}Config) -> Self {{
        {TemplateNameFirstCap}Addon {{ config }}
    }}
}}

impl PhoenixAddon for {TemplateNameFirstCap}Addon {{
    fn check_compatibility(&self, _prev: Option<&Version>) -> bool {{
        true
    }}

    fn decompose(self: Box<Self>) -> ResourceCollection {{
        let addon = *self;
        let mut collections = ResourceCollection::new();
        collections.insert("config".to_string(), Box::new(addon.config));
        collections
    }}

    #[inline]
    fn migrate(&mut self, _prev_addon: Box<dyn PhoenixAddon>) {{}}

    fn engines(&self) -> &[EngineType] {{
        {TemplateNameFirstCap}Addon::ENGINES
    }}

    fn update_config(&mut self, config: &str) -> Result<()> {{
        self.config = toml::from_str(config)?;
        Ok(())
    }}

    fn create_engine(
        &mut self,
        ty: EngineType,
        _pid: Pid,
        node: DataPathNode,
    ) -> Result<Box<dyn Engine>> {{
        if ty != {TemplateNameFirstCap}Addon::{TemplateNameAllCap}_ENGINE {{
            bail!("invalid engine type {{:?}}", ty)
        }}

        let builder = {TemplateNameFirstCap}EngineBuilder::new(node, self.config);
        let engine = builder.build()?;
        Ok(Box::new(engine))
    }}

    fn restore_engine(
        &mut self,
        ty: EngineType,
        local: ResourceCollection,
        node: DataPathNode,
        prev_version: Version,
    ) -> Result<Box<dyn Engine>> {{
        if ty != {TemplateNameFirstCap}Addon::{TemplateNameAllCap}_ENGINE {{
            bail!("invalid engine type {{:?}}", ty)
        }}

        let engine = {TemplateNameFirstCap}Engine::restore(local, node, prev_version)?;
        Ok(Box::new(engine))
    }}
}}
"""

engine_rs = """
use anyhow::{{anyhow, Result}};
use futures::future::BoxFuture;
use phoenix_api::rpc::{{RpcId, TransportStatus}};
use std::fmt;
use std::fs::File;
use std::io::Write;
use std::num::NonZeroU32;
use std::os::unix::ucred::UCred;
use std::pin::Pin;

use phoenix_api_policy_{TemplateName}::control_plane;


use phoenix_common::engine::datapath::message::{{
    EngineRxMessage, EngineTxMessage, RpcMessageGeneral,
}};

use phoenix_common::engine::datapath::node::DataPathNode;
use phoenix_common::engine::{{future, Decompose, Engine, EngineResult, Indicator, Vertex}};
use phoenix_common::envelop::ResourceDowncast;
use phoenix_common::impl_vertex_for_engine;
use phoenix_common::log;
use phoenix_common::module::Version;

use phoenix_common::storage::{{ResourceCollection, SharedStorage}};
use phoenix_common::engine::datapath::RpcMessageTx;

use super::DatapathError;
use crate::config::{{create_log_file, {TemplateNameCap}Config}};

{Include}

pub mod {ProtoDefinition} {{
    include!("proto.rs");
}}

{ProtoGetters}

{InternalStatesDefinition}

pub(crate) struct {TemplateNameCap}Engine {{
    pub(crate) node: DataPathNode,
    pub(crate) indicator: Indicator,
    pub(crate) config: {TemplateNameCap}Config,
    {InternalStatesInStructDefinition}
}}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Status {{
    Progress(usize),
    Disconnected,
}}

use Status::Progress;

impl Engine for {TemplateNameCap}Engine {{
    fn activate<'a>(self: Pin<&'a mut Self>) -> BoxFuture<'a, EngineResult> {{
        Box::pin(async move {{ self.get_mut().mainloop().await }})
    }}

    fn description(self: Pin<&Self>) -> String {{
        "{TemplateNameCap}Engine".to_owned()
    }}

    #[inline]
    fn tracker(self: Pin<&mut Self>) -> &mut Indicator {{
        &mut self.get_mut().indicator
    }}

    fn handle_request(&mut self, request: Vec<u8>, _cred: UCred) -> Result<()> {{
        let request: control_plane::Request = bincode::deserialize(&request[..])?;

        match request {{
            control_plane::Request::NewConfig() => {{
                self.config = {TemplateNameCap}Config {{}};
            }}
        }}
        Ok(())
    }}
}}

impl_vertex_for_engine!({TemplateNameCap}Engine, node);

impl Decompose for {TemplateNameCap}Engine {{
    fn flush(&mut self) -> Result<usize> {{
        let mut work = 0;
        while !self.tx_inputs()[0].is_empty() || !self.rx_inputs()[0].is_empty() {{
            if let Progress(n) = self.check_input_queue()? {{
                work += n;
            }}
        }}
        Ok(work)
    }}

    fn decompose(
        self: Box<Self>,
        _shared: &mut SharedStorage,
        _global: &mut ResourceCollection,
    ) -> (ResourceCollection, DataPathNode) {{
        let engine = *self;
        let mut collections = ResourceCollection::with_capacity(4);
        collections.insert("config".to_string(), Box::new(engine.config));
        (collections, engine.node)
        {InternalStatesOnDecompose}
    }}
}}

impl {TemplateNameCap}Engine {{
    pub(crate) fn restore(
        mut local: ResourceCollection,
        node: DataPathNode,
        _prev_version: Version,
    ) -> Result<Self> {{
        let config = *local
            .remove("config")
            .unwrap()
            .downcast::<{TemplateNameCap}Config>()
            .map_err(|x| anyhow!("fail to downcast, type_name={{:?}}", x.type_name()))?;
        {InternalStatesOnRestore}
        let engine = {TemplateNameCap}Engine {{
            node,
            indicator: Default::default(),
            config,
            {InternalStatesInConstructor}
        }};
        Ok(engine)
    }}
}}

impl {TemplateNameCap}Engine {{
    async fn mainloop(&mut self) -> EngineResult {{
        loop {{
            let mut work = 0;
            loop {{
                match self.check_input_queue()? {{
                    Progress(0) => break,
                    Progress(n) => work += n,
                    Status::Disconnected => return Ok(()),
                }}
            }}
            self.indicator.set_nwork(work);
            future::yield_now().await;
        }}
    }}
}}

#[inline]
fn materialize_nocopy(msg: &RpcMessageTx) -> &{ProtoRpcRequestType} {{
    let req_ptr = msg.addr_backend as *mut {ProtoRpcRequestType};
    let req = unsafe {{ req_ptr.as_ref().unwrap() }};
    return req;
}}

impl {TemplateNameCap}Engine {{
    fn check_input_queue(&mut self) -> Result<Status, DatapathError> {{
        use phoenix_common::engine::datapath::TryRecvError;

        match self.tx_inputs()[0].try_recv() {{
            Ok(msg) => {{
                match msg {{
                    EngineTxMessage::RpcMessage(msg) => {{
                        let meta_ref = unsafe {{ &*msg.meta_buf_ptr.as_meta_ptr() }};
                        let mut input = Vec::new();
                        input.push(msg);
                        {OnTxRpc}


                        for msg in output {{
                            match msg {{
                                RpcMessageGeneral::TxMessage(msg) => {{
                                    self.tx_outputs()[0].send(msg)?;
                                }}
                                RpcMessageGeneral::RxMessage(msg) => {{
                                    self.rx_outputs()[0].send(msg)?;
                                }}
                                _ => {{}}
                            }}
                        }}
                    }}
                    m => self.tx_outputs()[0].send(m)?,
                }}
                return Ok(Progress(1));
            }}
            Err(TryRecvError::Empty) => {{}}
            Err(TryRecvError::Disconnected) => {{
                return Ok(Status::Disconnected);
            }}
        }}

        match self.rx_inputs()[0].try_recv() {{
            Ok(msg) => {{
                match msg {{
                    EngineRxMessage::Ack(rpc_id, status) => {{
                        {OnRxRpc}
                        self.rx_outputs()[0].send(EngineRxMessage::Ack(rpc_id, status))?;
                    }}
                    EngineRxMessage::RpcMessage(msg) => {{
                        self.rx_outputs()[0].send(EngineRxMessage::RpcMessage(msg))?;
                    }}
                    m => self.rx_outputs()[0].send(m)?,
                }}
                return Ok(Progress(1));
            }}
            Err(TryRecvError::Empty) => {{}}
            Err(TryRecvError::Disconnected) => {{
                return Ok(Status::Disconnected);
            }}
        }}
        Ok(Progress(0))
    }}
}}
"""

proto_rs = r"""
///  The request message containing the user's name.
#[repr(C)]
#[derive(Debug, Clone, ::mrpc_derive::Message)]
pub struct HelloRequest {
    #[prost(bytes = "vec", tag = "1")]
    pub name: ::mrpc_marshal::shadow::Vec<u8>,
}
///  The response message containing the greetings
#[repr(C)]
#[derive(Debug, ::mrpc_derive::Message)]
pub struct HelloReply {
    #[prost(bytes = "vec", tag = "1")]
    pub message: ::mrpc_marshal::shadow::Vec<u8>,
}

// ///  The request message containing the user's name.
// #[repr(C)]
// #[derive(Debug, Clone, ::mrpc_derive::Message)]
// pub struct HelloRequest {
//     #[prost(bytes = "vec", tag = "1")]
//     pub name: ::mrpc::alloc::Vec<u8>,
// }
// ///  The response message containing the greetings
// #[repr(C)]
// #[derive(Debug, ::mrpc_derive::Message)]
// pub struct HelloReply {
//     #[prost(bytes = "vec", tag = "1")]
//     pub message: ::mrpc::alloc::Vec<u8>,
// }
"""

api_toml = """
[package]
name = "phoenix-api-policy-{TemplateName}"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
phoenix-api.workspace = true

serde.workspace = true
itertools.workspace = true
rand.workspace = true
"""

policy_toml = """
[package]
name = "phoenix-{TemplateName}"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
phoenix_common.workspace = true
phoenix-api-policy-{TemplateName}.workspace = true
mrpc-marshal.workspace = true
mrpc-derive.workspace = true
shm.workspace = true
phoenix-api = {{ workspace = true, features = ["mrpc"] }}

futures.workspace = true
minstant.workspace = true
thiserror.workspace = true
serde = {{ workspace = true, features = ["derive"] }}
serde_json.workspace = true
anyhow.workspace = true
nix.workspace = true
toml = {{ workspace = true, features = ["preserve_order"] }}
bincode.workspace = true
chrono.workspace = true
itertools.workspace = true
rand.workspace = true
"""


# prev = MrpcEngine, next = TcpRpcAdapterEngine
attach_toml = """
addon_engine = "{Me}Engine"
tx_channels_replacements = [
    [
        "{Prev}Engine",
        "{Me}Engine",
        0,
        0,
    ],
    [
        "{Me}Engine",
        "{Next}Engine",
        0,
        0,
    ],
]
rx_channels_replacements = [
    [
        "{Next}Engine",
        "{Me}Engine",
        0,
        0,
    ],
    [
        "{Me}Engine",
        "{Prev}Engine",
        0,
        0,
    ],
]
group = {Group}
op = "attach"
"""

detach_toml = """
addon_engine = "{Me}Engine"
tx_channels_replacements = [["{Prev}Engine", "{Next}Engine", 0, 0]]
rx_channels_replacements = [["{Next}Engine", "{Prev}Engine", 0, 0]]
op = "detach"

"""
