from compiler import *
from example import logging_sqls, acl_sqls, fault_sqls
import argparse
import os, re

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
    sql_statements = re.sub(r'--.*', '', sql_file_content).split(';')  # Remove -- comments and split statements

    # Remove empty statements and leading/trailing whitespace
    sql_statements = [statement.strip().replace("\n", " ") for statement in sql_statements if statement.strip()]

    compiler = ADNCompiler(verbose=False)


    print(f"Compiling {engine_name} statements...")
    ctx = init_ctx()
    for sql in sql_statements:
        rust_code = compiler.compile(sql, ctx)
        with open(f"./generated/{engine_name}.rs", "a") as f:
            f.write(rust_code + '\n')
        
        
    compiler.generate(engine_name)
    #os.system(f"rustfmt ./generated/{engine_name}_engine.rs")
    #os.system(f"cp ./generated/{engine_name}_engine.rs ./compiler_test/src/{engine_name}_engine.rs")
    