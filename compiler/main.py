from compiler import *
from example import logging_sqls, acl_sqls, fault_sqls
from codegen.codegen import *
import argparse
import os, re
from pprint import pprint

if __name__ == "__main__":
    os.system("rm -rf ./generated")
    os.system("mkdir -p ./generated")

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--engine', type=str, help='Engine name', required=True)
    args = parser.parse_args()
    engine_name = args.engine

    with open(f'../elements/{engine_name}.sql', 'r') as file:
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
    print(ast_init)
    print(ast_process)
    print("Compiling...")
    ctx = init_ctx()
    compiler.compile(ast, ctx)
    with open(f"./generated/{engine_name}.rs", "w") as f:
        f.write('\n'.join(ctx["code"]))

    
    # compiler.generate(engine_name)
    