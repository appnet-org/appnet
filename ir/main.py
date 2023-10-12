from ir.frontend import IRCompiler

if __name__ == "__main__":
    compiler = IRCompiler()
    
    with open("../elements/ir/acl.rs") as f:
        spec = f.read()
        print(spec)
        ir = compiler.compile(spec)
        print(ir)
        
        
        