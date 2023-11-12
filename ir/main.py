from ir.frontend import IRCompiler, Printer
from ir.props.flow import FlowGraph
import argparse
import os
import pathlib
import re
import sys
from pprint import pprint


if __name__ == "__main__":
    
        # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--engine", type=str, help="(Engine_name ',') *", required=True
    )
    parser.add_argument(
        "-v", "--verbose", help="Print Debug info", required=False, default=False
    )
    # parser.add_argument("--verbose", help="Print Debug info", action="store_true")
    # parser.add_argument(
    #     "--mrpc_dir",
    #     type=str,
    #     default=f"../../phoenix/experimental/mrpc",
    # )
    # parser.add_argument(
    #     "-o", "--output", type=str, help="Output type: ast, ir, mrpc", default="mrpc"
    # )
    args = parser.parse_args()
    engine = args.engine
    verbose = args.verbose  
    
    compiler = IRCompiler()
    printer = Printer()
    
    with open(f"../elements/ir/{engine}.rs") as f:
        spec = f.read()
        ir = compiler.compile(spec)
        p = ir.accept(printer, None)
        if verbose:
            print(p)
        
        
        req = FlowGraph().analyze(ir.req, verbose)
        resp = FlowGraph().analyze(ir.resp, verbose)
        
        yaml = "request:\n" + req.to_yaml() + "response:\n" + resp.to_yaml()
        print(yaml)
        