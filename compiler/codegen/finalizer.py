import os
import sys
from string import Formatter

from codegen.boilerplate import *
from codegen.context import *

from compiler.config import COMPILER_ROOT


# name: table_rpc_events
# type: Vec<struct_rpc_events>
# init: table_rpc_events = Vec::new()
#
def fill_internal_states(definition, declaration, name, type, init, process, proto):
    assert len(name) == len(type)
    proto_fc = proto[0].upper() + proto[1:]
    return {
        "ProtoDefinition": proto,
        # todo! field name should be configurable
        # todo! multiple type should be supported
        "ProtoGetters": f"""
fn {proto}_request_name_readonly(req: &{proto}::{proto_fc}Request) -> String {{
    let buf = &req.name as &[u8];
    String::from_utf8_lossy(buf).to_string().clone()
}}
        """,
        "ProtoRpcRequestType": f"{proto}::{proto_fc}Request",
        "ProtoRpcResponseType": f"{proto}::{proto_fc}Response",
        "InternalStatesDefinition": "".join(definition),
        "InternalStatesDeclaration": "".join(
            [f"use crate::engine::{i};\n" for i in declaration]
        ),
        "InternalStatesOnBuild": "".join(
            [f"let mut {i};\n" if "=" in i else f"{i};\n" for i in init]
        ),
        "InternalStatesOnRestore": "".join(
            [f"let mut {i};\n" if "=" in i else f"{i};\n" for i in init]
        ),
        "InternalStatesOnDecompose": "",
        "InternalStatesInConstructor": "".join([f"{i},\n" for i in name]),
        "InternalStatesInStructDefinition": "".join(
            [f"pub(crate) {i[0]}:{i[1]},\n" for i in zip(name, type)]
        ),
        "OnTxRpc": "".join(process),
        "OnRxRpc": r"""// todo """,
    }


def retrieve_info(ctx: Context):
    ctx.init_code = ctx.init_code[::-1]
    ctx.process_code = ctx.process_code[::-1]
    proto = "hello"
    proto_fc = "Hello"
    info = {
        "ProtoDefinition": proto,
        # todo! field name should be configurable
        # todo! multiple type should be supported
        "ProtoGetters": f"""
        """,
        "ProtoRpcRequestType": f"{proto}::{proto_fc}Request",
        "ProtoRpcResponseType": f"{proto}::{proto_fc}Response",
        "GlobalFunctionInclude": ctx.gen_global_function_includes(),
        "InternalStatesDefinition": "\n".join(ctx.def_code),
        "InternalStatesDeclaration": "\n".join(
            [f"use crate::engine::{i};" for i in ctx.gen_struct_names()]
        ),
        "InternalStatesOnBuild": "\n".join(ctx.gen_init_localvar())
        + "\n".join(ctx.init_code),
        "InternalStatesOnRestore": "\n".join(ctx.gen_init_localvar())
        + "\n".join(ctx.init_code),
        "InternalStatesOnDecompose": "",
        "InternalStatesInConstructor": "\n".join(
            [f"{i}," for i in ctx.gen_var_names()]
        ),
        "InternalStatesInStructDefinition": "\n".join(
            [f"pub(crate) {i}," for i in ctx.gen_struct_declaration()]
        ),
        "OnTxRpc": "".join(ctx.process_code),
        "OnRxRpc": r"""// todo """,
    }
    # for k,v in info.items():
    #     print(k)
    #     print(v)
    return info


def parse_intermediate_code(name):
    ctx = {
        "definition": [],
        "declaration": [],
        "internal": [],
        "init": [],
        "name": [],
        "type": [],
        "process": [],
    }
    print("Generating code for " + name)
    with open(os.path.join(COMPILER_ROOT, f"generated/{name}.rs")) as f:
        current = "process"
        for i in f.readlines():
            if i.startswith("///@@"):
                j = i.split()
                if j[1] == "BEG_OF":
                    if j[2] == "declaration":
                        current = "declaration"
                    elif j[2] == "internal":
                        print("Warning: No Internal Should Be Generated")
                        current = "internal"
                    elif j[2] == "init":
                        current = "init"
                    elif j[2] == "process":
                        current = "process"
                    elif j[2] == "type":
                        current = "type"
                    elif j[2] == "name":
                        current = "name"
                    elif j[2] == "definition":
                        current = "definition"
                elif j[1] == "END_OF":
                    assert j[2] == current
                    current = "process"
            else:
                if current is not None:
                    if i.strip() != "":
                        ctx[current].append(i.strip("\n"))

    ctx = fill_internal_states(
        ctx["definition"],
        ctx["declaration"],
        ctx["name"],
        ctx["type"],
        ctx["init"],
        ctx["process"],
        "hello",
    )

    return ctx


def gen_template(
    ctx,
    template_name,
    template_name_toml,
    template_name_first_cap,
    template_name_all_cap,
):
    target_dir = os.path.join(COMPILER_ROOT, f"generated/{template_name}")
    os.system(f"rm -rf {target_dir}")
    os.system(f"mkdir -p {target_dir}")
    os.chdir(target_dir)
    ctx["TemplateName"] = template_name
    ctx["TemplateNameFirstCap"] = template_name_first_cap
    ctx["TemplateNameAllCap"] = template_name_all_cap
    ctx["TemplateNameCap"] = template_name_first_cap
    # print("Current dir: {}".format(os.getcwd()))
    with open("config.rs", "w") as f:
        f.write(config_rs.format(Include=include, **ctx))
    with open("lib.rs", "w") as f:
        f.write(lib_rs.format(Include=include, **ctx))
    with open("module.rs", "w") as f:
        f.write(module_rs.format(Include=include, **ctx))
    with open("engine.rs", "w") as f:
        # print([i[1] for i in Formatter().parse(engine_rs)  if i[1] is not None])
        f.write(engine_rs.format(Include=include, **ctx))
    with open("proto.rs", "w") as f:
        f.write(proto_rs)
    with open("Cargo.toml.api", "w") as f:
        f.write(api_toml.format(TemplateName=template_name_toml))
    with open("Cargo.toml.policy", "w") as f:
        f.write(policy_toml.format(TemplateName=template_name_toml))
    print("Template {} generated".format(template_name))


def move_template(
    mrpc_root, template_name, template_name_toml, template_name_first_cap
):
    mrpc_api = mrpc_root + "/generated/api"
    original_api = mrpc_root + "/phoenix-api/policy"

    os.system("mkdir -p {}".format(mrpc_api))

    os.system(f"rm -rf {mrpc_api}/{template_name_toml}")
    os.system(f"cp -r {original_api}/logging {mrpc_api}/{template_name_toml}")
    os.system(f"rm {mrpc_api}/{template_name_toml}/Cargo.toml")
    os.system(f"cp ./Cargo.toml.api {mrpc_api}/{template_name_toml}/Cargo.toml")

    mrpc_plugin = mrpc_root + "/generated/plugin"
    os.system("mkdir -p {}".format(mrpc_plugin))

    os.system(f"rm -rf {mrpc_plugin}/{template_name_toml}")
    os.system(f"mkdir -p {mrpc_plugin}/{template_name_toml}/src")
    os.system(f"cp ./Cargo.toml.policy {mrpc_plugin}/{template_name_toml}/Cargo.toml")

    os.system(f"rustfmt --edition 2018  ./config.rs")
    os.system(f"rustfmt --edition 2018  ./lib.rs")
    os.system(f"rustfmt --edition 2018  ./module.rs")
    os.system(f"rustfmt --edition 2018  ./engine.rs")
    os.system(f"rustfmt --edition 2018  ./proto.rs")
    os.system(f"cp ./config.rs {mrpc_plugin}/{template_name_toml}/src/config.rs")
    os.system(f"cp ./lib.rs {mrpc_plugin}/{template_name_toml}/src/lib.rs")
    os.system(f"cp ./module.rs {mrpc_plugin}/{template_name_toml}/src/module.rs")
    os.system(f"cp ./engine.rs {mrpc_plugin}/{template_name_toml}/src/engine.rs")
    os.system(f"cp ./proto.rs {mrpc_plugin}/{template_name_toml}/src/proto.rs")
    print("Template {} moved to mrpc folder".format(template_name))


def gen_attach_detach(name: str, ctx):
    with open(f"{name}_attach.toml", "w") as f:
        f.write(attach_toml.format(**ctx))

    with open(f"{name}_detach.toml", "w") as f:
        f.write(detach_toml.format(**ctx))


def finalize(name: str, ctx: Context, output_dir: str):
    if name == "logging":
        # template_name = "nofile_logging"
        # template_name_toml = "nofile-logging"
        # template_name_first_cap = "NofileLogging"
        # template_name_all_cap = "NOFILE_LOGGING"
        template_name = "file_logging"
        template_name_toml = "file-logging"
        template_name_first_cap = "FileLogging"
        template_name_all_cap = "FILE_LOGGING"
    elif name == "acl":
        template_name = "hello_acl"
        template_name_toml = "hello-acl"
        template_name_first_cap = "HelloAcl"
        template_name_all_cap = "HELLO_ACL"
    elif name == "fault":
        template_name = "fault"
        template_name_toml = "fault"
        template_name_first_cap = "Fault"
        template_name_all_cap = "FAULT"
    else:
        name = name.split("_")
        template_name = "_".join(name)
        template_name_toml = "-".join(name)
        cap = [i[0].upper() + i[1:] for i in name]
        template_name_first_cap = "".join(cap)
        template_name_all_cap = "_".join(name).upper()

    # ctx.explain()
    info = retrieve_info(ctx)
    gen_template(
        info,
        template_name,
        template_name_toml,
        template_name_first_cap,
        template_name_all_cap,
    )
    move_template(
        output_dir,
        template_name,
        template_name_toml,
        template_name_first_cap,
    )


def finalize_graph(ctx: Dict[str, object], mrpc_dir: str):
    output_dir = f"{mrpc_dir}/generated"
    os.chdir(COMPILER_ROOT)

    os.system("rm -rf ./generated/addonctl")
    os.system("mkdir ./generated/addonctl")
    os.chdir("./generated/addonctl")
    for k, v in ctx.items():
        gen_attach_detach(k, v)
        print(f"Generated {k} attach/detach toml")
    os.chdir(COMPILER_ROOT)

    os.system(f"rm -rf {output_dir}/addonctl")
    os.system(f"mkdir -p {output_dir}/addonctl")
    os.system(f"cp -r ./generated/addonctl {output_dir}/")
