from compile import *
from compiler import *
from example import logging_sqls, acl_sqls, fault_sqls
from codegen.template import generate
import os

if __name__ == "__main__":
    os.system("mkdir -p ./generated")
    os.system("rm -f ./generated/*")
    compiler = ADNCompiler(verbose=False)
    
    logging_asts = [compiler.transform(sql) for sql in logging_sqls]
    print("Compiling logging statements...")

    ctx = init_ctx()
    for ast in logging_asts:
        rust_code = compile_sql_to_rust(ast, ctx)
        with open("./generated/logging.rs", "a") as f:
            f.write(rust_code + '\n')

    acl_asts = [compiler.transform(sql) for sql in acl_sqls]
    print("Compiling acl statements...")
    ctx = init_ctx()
    for ast in acl_asts:
        rust_code = compile_sql_to_rust(ast, ctx)
        #print(rust_code)
        with open("./generated/acl.rs", "a") as f:
            f.write(rust_code + '\n')
    
    fault_asts = [compiler.transform(sql) for sql in fault_sqls]
    print()
    print("Compiling fault statements...")
    ctx = init_ctx()
    for ast in fault_asts:
        rust_code = compile_sql_to_rust(ast, ctx)
        #print(rust_code)
        with open("./generated/fault.rs", "a") as f:
            f.write(rust_code + '\n')
    
    engines = ["logging", "acl", "fault"]        
    for e in engines:
        generate(e)
        os.system(f"rustfmt ./generated/{e}_engine.rs")
        os.system(f"cp ./generated/{e}_engine.rs ./compiler_test/src/{e}_engine.rs")
    