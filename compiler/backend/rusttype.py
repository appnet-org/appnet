from __future__ import annotations
from typing import List, Optional
from enum import Enum
import copy
from backend.abstract import BackendVariable, BackendType
from codegen.context import SQLVariable

class RustType(BackendType):
    def __init__(self, name: str):
        self.name = name
        
    def is_basic(self) -> bool:
        return False

    def __str__(self) -> str:
        return self.name
    
    def __iter__(self):
        return [self]
    
    def gen_init() -> str:
        raise NotImplementedError()
        
class RustBasicType(RustType):
    """
    Everything that is not struct, but also is not something with template parameters
    
    Like usize, String, File, etc.
    
    We use default init value, or use provided init value
    """
    def __init__(self, name: str, init_val: Optional[str]):
        super().__init__(name)
        self.init_val = init_val
         
    def is_basic(self) -> bool:
        return True
    
    def gen_init(self) -> str:
        if self.init_val is None:
            return f"{self.name}::default()"
        else:
            return self.init_val
        
class RustContainerType(RustType):
    """
    A better name should be RustTemplateType
    
    Everything that is Con<Elem>, like Vec<usize> ...
    
    Currently, we only support Vec<TypeName>
    """
    def __init__(self, con: str, elem: RustType) -> None:
        super().__init__(f"{con}<{elem.name}>")
        self.con = con
        self.elem = elem
        
    def gen_init(self) -> str:
        return f"{self.con}::new()"

class RustStructType(RustType):
    def __init__(self, name: str, fields: List[(str, RustType)]):
        super().__init__(name)
        self.fields = fields
     
    def __str__(self) -> str:
        return f"struct {self.name} {{\n" + "\n".join([f"    {i}: {j}," for i, j in self.fields]) + "\n}"
    
    def __iter__(self):
        return iter(self.fields)
    
    # all pub by default    
    def gen_definition(self) -> str:
        return f"pub struct {self.name} {{\n" + "\n".join([f"    pub {i}: {j.name}," for i, j in self.fields]) + "\n}"
    
    def gen_copy_constructor(self) -> str:
        return f"impl {self.name} {{\n" + f"    pub fn new({', '.join([f'{i}: {j.name}' for i, j in self.fields])}) -> {self.name} {{\n" + f"        {self.name} {{\n" + "\n".join([f"            {i}: {i}," for i, j in self.fields]) + "\n        }\n    }\n}\n"
        
    def gen_trait_display(self) -> str:
        ret =  f"impl fmt::Display for {self.name} {{\n" + f"    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {{\n"
        for i, j in self.fields:
            ret += f"        write!(f, \"{{}}\", self.{i});\n"
        ret += "    }\n"
        ret += "}\n"
        
class RustVariable(BackendVariable):
    def __init__(self, name: str, rust_type: RustType, mut: bool, parent: SQLVariable) -> None:
        self.name = name
        self.type = rust_type
        self.mut = mut
        self.parent = parent
    
    def __str__(self) -> str:
        return f"{'mut ' if self.mut else ''}{self.name}: {self.type}"
    
    
tx_struct = RustStructType("RpcMessageTx", [("meta_buf_ptr", RustStructType("MetaBufferPtr", [])), ("addr_backend", RustBasicType("usize"))])

# rx_struct = RustStructType("RpcMessageRx", [("meta_buf_ptr", RustStructType("MetaBufferPtr", [])), ("addr_backend", RustBasicType("usize"))])

