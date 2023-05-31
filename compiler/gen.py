
import sys


template="""
use crate::engine::Engine;
use crate::engine::RpcMessage;
use chrono::prelude::*;
use itertools::iproduct;
{declaration}

pub struct {engine_name} {{
    {internal}
}}


impl Engine for {engine_name} {{
    fn init(&mut self) {{
        {init}
    }}
    fn process(&mut self, input: Vec<RpcMessage>) -> Vec<RpcMessage> {{
        {process}
        output
    }}
}}
"""


if __name__ == "__main__":
    ctx = {
        "declaration": [],
        "internal": [],
        "init": [],
        "process": [],
    }
    name = sys.argv[1].strip(".rs") + "_engine"
    print(name)
    with open("./generated/" + sys.argv[1]) as f:
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
            else:
                if current is not None:
                    if i.strip() != "":
                        ctx[current].append(i)
    
    print(ctx)
    
    with open("./generated/" + name + ".rs", "w") as f:
        f.write(template.format(
            declaration="".join(ctx["declaration"]),
            internal="".join(ctx["internal"]),
            init="".join(ctx["init"]),
            process="".join(ctx["process"]),
            engine_name=name,
        ))