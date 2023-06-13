
import sys
import os
from codegen.boilerplate import *
from string import Formatter

# name: table_rpc_events
# type: Vec<struct_rpc_events>
# init: table_rpc_events = Vec::new()
#
def fill_internal_states(declaration, name, type, init, process):
    return {
        "InternalStatesDeclaration": declaration,
        "InternalStatesOnBuild": f"let mut {init};\n ",
        "InternalStatesOnRestore": f"let mut {init};\n",
        "InternalStatesOnDecompose": "",
        "InternalStatesInConstructor": f"{name},",
        "InternalStatesInStructDeclaration": f"pub(crate) {name}:{type},",
        "OnTxRpc": process,
        "OnRxRpc": r"""// todo """ 
    }


def parse_intermediate_code(name):
    ctx = {
        "declaration": [],
        "internal": [],
        "init": [],
        "name": [],
        "type": [],
        "process": [],
    }
    print("Generating code for " + name)
    with open("./generated/" + name + ".rs") as f:
        current = "process"
        for i in f.readlines():
            if i.startswith("///@@"):
                j = i.split()
                if j[1] == "BEG_OF":
                    if j[2] == "declaration":
                        current = "declaration"
                    elif j[2] == "internal":
                        current = "internal"
                    elif j[2] == "init":
                        current = "init"
                    elif j[2] == "process":
                        current = "process"
                    elif j[2] == "type":
                        current = "type"
                    elif j[2] == "name":
                        current = "name"
            else:
                if current is not None:
                    if i.strip() != "":
                        ctx[current].append(i)
    
    ctx = fill_internal_states("".join(ctx["declaration"]), "".join(ctx["name"]), "".join(ctx["type"]), "".join(ctx["init"]), "".join(ctx["process"]))
    
    return ctx
        

def gen_template(ctx, template_name, template_name_toml, template_name_first_cap, template_name_all_cap):
    target_dir = "./generated/{}".format(template_name)
    os.system(f"rm -rf {target_dir}")
    os.system(f"mkdir -p {target_dir}")
    os.chdir(target_dir)
    ctx["TemplateName"] = template_name
    ctx["TemplateNameFirstCap"] = template_name_first_cap
    ctx["TemplateNameAllCap"] = template_name_all_cap
    ctx["TemplateNameCap"] = template_name_first_cap
    print("Current dir: {}".format(os.getcwd()))
    with open("config.rs", "w") as f:
        f.write(config_rs.format(Include=include, **ctx))
    with open("lib.rs", "w") as f:
        f.write(lib_rs.format(Include=include, **ctx))
    with open("module.rs", "w") as f:
        f.write(module_rs.format(Include=include, **ctx))
    with open("engine.rs", "w") as f:
        #print([i[1] for i in Formatter().parse(engine_rs)  if i[1] is not None])
        f.write(engine_rs.format(Include=include, **ctx))
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
    
    os.system(f"rustfmt --edition 2018  ./config.rs")
    os.system(f"rustfmt --edition 2018  ./lib.rs")
    os.system(f"rustfmt --edition 2018  ./module.rs")
    os.system(f"rustfmt --edition 2018  ./engine.rs")
    os.system(f"cp ./config.rs {mrpc_plugin}/{template_name_toml}/src/config.rs")
    os.system(f"cp ./lib.rs {mrpc_plugin}/{template_name_toml}/src/lib.rs")
    os.system(f"cp ./module.rs {mrpc_plugin}/{template_name_toml}/src/module.rs")
    os.system(f"cp ./engine.rs {mrpc_plugin}/{template_name_toml}/src/engine.rs") 
    print("Template {} moved to mrpc folder".format(template_name))
    
def generate(name):
    if name != "logging":
        raise ValueError("Only logging is supported")
    template_name = "nofile_logging"
    template_name_toml = "nofile-logging"
    template_name_first_cap = "NofileLogging"
    template_name_all_cap = "NOFILE_LOGGING"
    ctx = parse_intermediate_code("logging")
    gen_template(ctx, template_name, template_name_toml, template_name_first_cap, template_name_all_cap)
    move_template("/users/banruo/phoenix/experimental/mrpc", template_name, template_name_toml, template_name_first_cap)
    

    
    
    