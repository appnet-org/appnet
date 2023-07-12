import argparse
import os
import pathlib
import re
import sys

from pprint import pprint

from adn_compiler import ADNCompiler
from codegen.codegen import *
from config import ADN_ROOT
from example import acl_sqls, fault_sqls, logging_sqls
from frontend.visitor import *
if __name__ == "__main__":
    os.system("rm -rf ./generated")
    os.system("mkdir -p ./generated")

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--engine", type=str, help="Engine name", required=True)
    parser.add_argument("--verbose", help="Print Lark info", action="store_true")
    args = parser.parse_args()
    engine_name = args.engine

    with open(os.path.join(ADN_ROOT, f"elements/{engine_name}.sql"), "r") as file:
        sql_file_content = file.read()

    # Remove comments from the SQL file
    sql_file_content = re.sub(r'/\*.*?\*/', '', sql_file_content, flags=re.DOTALL)  # Remove /* ... */ comments
    sql_statements = sql_file_content.split('--processing--')
    sql_statements = [re.sub(r'--.*', '', i) for i in sql_statements] # Remove -- comments and split statements
    # Remove empty statements and leading/trailing whitespace
    compiler = ADNCompiler(verbose=False)
    ast_init = compiler.transform(sql_statements[0])
    ast_process = compiler.transform(sql_statements[1])
    print("Transformed AST")
    #printer = Printer()
    #printer.visitRoot(ast_init, 2)
    #printer.visitRoot(ast_process, 2)
    print("Compiling...")
    ctx = init_ctx()
    compiler.compile(ast_init, ctx)
    compiler.compile(ast_process, ctx)

    print("Generating intermidiate code...")
    with open(f"./generated/{engine_name}.rs", "w") as f:
        f.write('\n'.join(ctx.def_code))
        f.write('\n'.join(ctx.init_code))
        f.write('\n'.join(ctx.process_code))

    
    compiler.generate(engine_name, ctx)
    
