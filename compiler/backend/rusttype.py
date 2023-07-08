from __future__ import annotations
from typing import List, Optional
from enum import Enum
import copy
from codegen.context import SQLVariable


class RustType():
    def __init__(self, name: str):
        self.name = name
        
    def is_basic(self) -> bool:
        return False

    def __str__(self) -> str:
        return self.name

class RustBasicType(RustType):
    def __init__(self, name: str):
        super().__init__(name)
        
    def is_basic(self) -> bool:
        return True
    
class RustContainerType(Enum):
    def __init__(self, cname: str, tname: str) -> None:
        super().__init__(f"{cname}<{tname}>")
        self.cname = cname
        self.tname = tname

class RustStructType(RustType):
    def __init__(self, name: str, fields: List[(str, RustType)]):
        super().__init__(name)
        self.fields = fields
     
    def __str__(self) -> str:
        return f"struct {self.name} {{\n" + "\n".join([f"    {i}: {j}," for i, j in self.fields]) + "\n}"
        
class RustVariable():
    def __init__(self, name: str, rust_type: RustType, mut: bool, parent: SQLVariable) -> None:
        self.name = name
        self.type = rust_type
        self.mut = mut
        self.parent = parent
    
    def __str__(self) -> str:
        return f"{'mut ' if self.mut else ''}{self.name}: {self.type}"