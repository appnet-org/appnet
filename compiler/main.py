import argparse
import os
import re
from pprint import pprint

from codegen.codegen import *
from example import acl_sqls, fault_sqls, logging_sqls

from compiler import *

if __name__ == "__main__":
    os.system("rm -rf ./generated")
    os.system("mkdir -p ./generated")

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--engine", type=str, help="Engine name", required=True)
    args = parser.parse_args()
    engine_name = args.engine

    with open(f"../elements/{engine_name}.sql", "r") as file:
        sql_file_content = file.read()

    # Remove comments from the SQL file
    sql_file_content = re.sub(
        r"/\*.*?\*/", "", sql_file_content, flags=re.DOTALL
    )  # Remove /* ... */ comments
    sql_statements = re.sub(
        r"--.*", "", sql_file_content
    )  # Remove -- comments and split statements
    print(sql_statements)
    # Remove empty statements and leading/trailing whitespace

    compiler = ADNCompiler(verbose=False)
    ast = compiler.transform(sql_statements)
    print("Transformed AST")

    print("Compiling...")
    ctx = init_ctx()
    compiler.compile(ast, ctx)
    with open(f"./generated/{engine_name}.rs", "w") as f:
        f.write("\n".join(ctx["code"]))

    compiler.generate(engine_name)
