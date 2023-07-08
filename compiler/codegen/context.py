from __future__ import annotations
from typing import List, Optional
from enum import Enum
import copy
from backend.rusttype import *

class SQLVariable():
    def __init__(self, name: str):
        self.name = name
        
class Column(SQLVariable):
    def __init__(self, tname: str, cname: str, dtype: str):
        super().__init__(f"{tname}.{cname}")
        self.tname = tname
        self.cname = cname
        self.dtype = dtype

class Table(SQLVariable):
    def __init__(self, name: str, columns: List[Column]):
        super().__init__(name)
        self.columns = columns
        

class Context():
    def __init__(self, tables: List[Table], rust_vars: List[RustVariable]):
        self.def_code = []
        self.init_code = []
        self.process_code = []
        self.tables = {}
        for i in tables:
            self.tables[i.name] = i
        self.sql_vars = {}
        self.rust_vars = {}
        
InputTable = Table("input", [Column("input", "type", "string"), Column("input", "src", "string"), Column("input", "dst", "string"), Column("input", "payload", "protobuf")])

OutputTable = Table("output", [Column("output", "type", "string"), Column("output", "src", "string"), Column("output", "dst", "string"), Column("output", "payload", "protobuf")])

