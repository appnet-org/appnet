from compiler import *
from example import logging_sqls, acl_sqls, fault_sqls
import os

if __name__ == "__main__":
    os.system("mkdir -p ./generated")
    os.system("rm -f ./generated/*")
    compiler = ADNCompiler(verbose=False)

    print("Compiling logging statements...")
    ctx = init_ctx()
    for ast in logging_sqls:
        rust_code = compiler.compile(ast, ctx)
        with open("./generated/logging.rs", "a") as f:
            f.write(rust_code + '\n')

    print("Compiling acl statements...")
    ctx = init_ctx()
    for ast in acl_sqls:
        rust_code = compiler.compile(ast, ctx)
        #print(rust_code)
        with open("./generated/acl.rs", "a") as f:
            f.write(rust_code + '\n')
    
    print()
    print("Compiling fault statements...")
    ctx = init_ctx()
    for ast in fault_sqls:
        rust_code = compiler.compile(ast, ctx)
        #print(rust_code)
        with open("./generated/fault.rs", "a") as f:
            f.write(rust_code + '\n')
    
    engines = ["logging", "acl", "fault"]        
    for e in engines:
        compiler.generate(e)
        os.system(f"rustfmt ./generated/{e}_engine.rs")
        os.system(f"cp ./generated/{e}_engine.rs ./compiler_test/src/{e}_engine.rs")
    