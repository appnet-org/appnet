from ir.frontend import IRCompiler
import argparse
import os
import pathlib
import re
import sys

if __name__ == "__main__":
    compiler = IRCompiler()
    
        # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--engine", type=str, help="(Engine_name ',') *", required=True
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
    with open(f"../elements/ir/{engine}.rs") as f:
        spec = f.read()
        print(spec)
        ir = compiler.compile(spec)
        print(ir)
        
        
        