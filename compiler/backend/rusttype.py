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
    
class RustBasicType(RustType):
    def __init__(self, name: str):
        super().__init__(name)
        
    def is_basic(self) -> bool:
        return True
    
class RustContainerType(RustType):
    def __init__(self, con: str, elem: RustType) -> None:
        super().__init__(f"{con}<{elem.name}>")
        self.con = con
        self.elem = elem

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

