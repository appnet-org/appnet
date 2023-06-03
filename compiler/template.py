import os

# template_name = "{TemplateName}"

config_rs="""
use chrono::{{Datelike, Timelike, Utc}};
use phoenix_common::log;
use serde::{{Deserialize, Serialize}};

#[derive(Debug, Clone, Copy, Default, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct {TemplateName}Config {{}}


impl {TemplateName}Config {{
    /// Get config from toml file
    pub fn new(config: Option<&str>) -> anyhow::Result<Self> {{
        let config = toml::from_str(config.unwrap_or(""))?;
        Ok(config)
    }}
}}
"""

lib_rs="""
#![feature(peer_credentials_unix_socket)]
use thiserror::Error;

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

use crate::config::{TemplateName}Config;
use crate::module::{TemplateName}Addon;

#[no_mangle]
pub fn init_addon(config_string: Option<&str>) -> InitFnResult<Box<dyn PhoenixAddon>> {{
    let config = {TemplateName}Config::new(config_string)?;
    let addon = {TemplateName}Addon::new(config);
    Ok(Box::new(addon))
}}
"""

module_rs="""
use anyhow::{{bail, Result}};
use nix::unistd::Pid;

use phoenix_common::addon::{{PhoenixAddon, Version}};
use phoenix_common::engine::datapath::DataPathNode;
use phoenix_common::engine::{{Engine, EngineType}};
use phoenix_common::storage::ResourceCollection;

use super::engine::{TemplateName}Engine;
use crate::config::{TemplateName}Config;

pub(crate) struct {TemplateName}EngineBuilder {{
    node: DataPathNode,
    config: {TemplateName}Config,
}}

impl {TemplateName}EngineBuilder {{
    fn new(node: DataPathNode, config: {TemplateName}Config) -> Self {{
        {TemplateName}EngineBuilder {{ node, config }}
    }}
    // TODO! LogFile
    fn build(self) -> Result<{TemplateName}Engine> {{

        Ok({TemplateName}Engine {{
            node: self.node,
            indicator: Default::default(),
            config: self.config,
        }})
    }}
}}

pub struct {TemplateName}Addon {{
    config: {TemplateName}Config,
}}

impl {TemplateName}Addon {{
    pub const {TemplateName}_ENGINE: EngineType = EngineType("{TemplateName}Engine");
    pub const ENGINES: &'static [EngineType] = &[{TemplateName}Addon::{TemplateName}_ENGINE];
}}

impl {TemplateName}Addon {{
    pub fn new(config: {TemplateName}Config) -> Self {{
        {TemplateName}Addon {{ config }}
    }}
}}

impl PhoenixAddon for {TemplateName}Addon {{
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
        {TemplateName}Addon::ENGINES
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
        if ty != {TemplateName}Addon::{TemplateName}_ENGINE {{
            bail!("invalid engine type {{:?}}", ty)
        }}

        let builder = {TemplateName}EngineBuilder::new(node, self.config);
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
        if ty != {TemplateName}Addon::{TemplateName}_ENGINE {{
            bail!("invalid engine type {{:?}}", ty)
        }}

        let engine = {TemplateName}Engine::restore(local, node, prev_version)?;
        Ok(Box::new(engine))
    }}
}}
"""

engine_rs="""
use anyhow::{{anyhow, Result}};
use futures::future::BoxFuture;
use std::io::Write;
use std::os::unix::ucred::UCred;
use std::pin::Pin;

use phoenix_api_policy_{TemplateName}::control_plane;

use phoenix_common::engine::datapath::message::{{EngineRxMessage, EngineTxMessage}};

use phoenix_common::engine::datapath::node::DataPathNode;
use phoenix_common::engine::{{future, Decompose, Engine, EngineResult, Indicator, Vertex}};
use phoenix_common::envelop::ResourceDowncast;
use phoenix_common::impl_vertex_for_engine;
use phoenix_common::module::Version;
use phoenix_common::storage::{{ResourceCollection, SharedStorage}};

use super::DatapathError;
use crate::config::{{{TemplateNameCap}Config}};

pub(crate) struct {TemplateNameCap}Engine {{
    pub(crate) node: DataPathNode,
    pub(crate) indicator: Indicator,
    pub(crate) config: {TemplateNameCap}Config,
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

        let engine = {TemplateNameCap}Engine {{
            node,
            indicator: Default::default(),
            config,
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

impl {TemplateNameCap}Engine {{
    fn check_input_queue(&mut self) -> Result<Status, DatapathError> {{
        use phoenix_common::engine::datapath::TryRecvError;

        match self.tx_inputs()[0].try_recv() {{
            Ok(msg) => {{
                match msg {{
                    EngineTxMessage::RpcMessage(msg) => {{
                        
                        let meta_ref = unsafe {{ &*msg.meta_buf_ptr.as_meta_ptr() }};

                        // TODO! write to file
                        
                        self.tx_outputs()[0].send(EngineTxMessage::RpcMessage(msg))?;
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
                        // TODO! write to file
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

api_toml="""
[package]
name = "phoenix-api-policy-{TemplateName}"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
phoenix-api.workspace = true

serde.workspace = true
"""

policy_toml="""
[package]
name = "phoenix-{TemplateName}"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
phoenix_common.workspace = true
phoenix-api-policy-{TemplateName}.workspace = true

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
"""

def gen_template(template_name, template_name_toml, template_name_first_cap):
    target_dir = "./generated/{}".format(template_name)
    os.system(f"rm -rf {target_dir}")
    os.system(f"mkdir -p {target_dir}")
    os.chdir(target_dir)
    print("Current dir: {}".format(os.getcwd()))
    with open("config.rs", "w") as f:
        f.write(config_rs.format(TemplateName=template_name_first_cap))
    with open("lib.rs", "w") as f:
        f.write(lib_rs.format(TemplateName=template_name_first_cap))
    with open("module.rs", "w") as f:
        f.write(module_rs.format(TemplateName=template_name_first_cap))
    with open("engine.rs", "w") as f:
        f.write(engine_rs.format(TemplateNameCap=template_name_first_cap, TemplateName=template_name))
    with open("Cargo.toml.api", "w") as f:
        f.write(api_toml.format(TemplateName=template_name_toml))
    with open("Cargo.toml.policy", "w") as f:
        f.write(policy_toml.format(TemplateName=template_name_toml))
    print("Template {} generated".format(template_name))

def move_template(mrpc_root, template_name, template_name_toml, template_name_first_cap):
    mrpc_api = mrpc_root + "/phoenix-api/policy/";
    os.system(f"rm -rf {mrpc_api}/{template_name_toml}")
    os.system(f"cp -r {mrpc_api}/logging {mrpc_api}/{template_name_toml}")
    os.system(f"rm {mrpc_api}/{template_name_toml}/Cargo.toml")
    os.system(f"cp ./Cargo.toml.api {mrpc_api}/{template_name_toml}/Cargo.toml")
    mrpc_plugin = mrpc_root + "/plugin/policy";
    os.system(f"rm -rf {mrpc_plugin}/{template_name_toml}")
    os.system(f"mkdir -p {mrpc_plugin}/{template_name_toml}/src")  
    os.system(f"cp ./Cargo.toml.policy {mrpc_plugin}/{template_name_toml}/Cargo.toml") 
    os.system(f"cp ./config.rs {mrpc_plugin}/{template_name_toml}/src/config.rs")
    os.system(f"cp ./lib.rs {mrpc_plugin}/{template_name_toml}/src/lib.rs")
    os.system(f"cp ./module.rs {mrpc_plugin}/{template_name_toml}/src/module.rs")
    os.system(f"cp ./engine.rs {mrpc_plugin}/{template_name_toml}/src/engine.rs") 
    print("Template {} moved".format(template_name))
    
if __name__ == "__main__":
    template_name = "nofile_logging"
    template_name_toml = "nofile-logging"
    template_name_first_cap = "NofileLogging"
    gen_template(template_name, template_name_toml, template_name_first_cap)
    move_template("/users/banruo/phoenix/experimental/mrpc", template_name, template_name_toml, template_name_first_cap)
    

    
    
    