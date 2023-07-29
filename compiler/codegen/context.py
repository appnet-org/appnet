from __future__ import annotations

import copy
from enum import Enum
from typing import Dict, List, Optional

from backend.abstract import *

from compiler.protobuf.protobuf import Proto


class SQLVariable:
    def __init__(self, name: str):
        self.name = name


class Column(SQLVariable):
    def __init__(self, tname: str, cname: str, dtype: str):
        super().__init__(f"{tname}.{cname}")
        self.tname = tname
        self.cname = cname
        self.dtype = dtype


class Table(SQLVariable):
    def __init__(self, name: str, columns: List[Column], struct: BackendType):
        super().__init__(name)
        self.columns = columns
        self.struct = struct


class Context:
    def __init__(
        self, tables: List[Table], rust_vars: List[BackendVariable], proto: Proto
    ):
        self._def_code = []
        self._init_code = []
        self._process_code = []
        self._tables = {}
        self._temp_code = []
        for i in tables:
            self._tables[i.name] = i
        self._sql_vars = {}
        self._rust_vars = {}
        self._temp_vars = {}
        self.is_forward = False
        self.proto = proto
        self.name_mapping: Dict[str, str] = {}
        self.current: str = "init"
        self.global_func = None

    def explain(self):
        print("Context.Explain:")
        print("Tables:")
        for i in self.tables.values():
            print("\t", i.name)
            print("\t\t", i.struct.name)
        # print(i.columns)

        print("SQL Vars:")
        for i in self.sql_vars.values():
            print("\t", i.name)

        print("Rust Vars:")
        for i in self.rust_vars.values():
            print("\t", i.name)
            if i.parent is not None:
                print("\t\t", i.parent.name)
            print("\t\ttype:", i.type)
            print("\t\tinit_val:", i.init)

    def gen_struct_names(self) -> List[str]:
        ret = []
        for i in self.tables.values():
            if i.name == "input" or i.name == "output":
                continue
            ret.append(i.struct.name)
        return ret

    def gen_var_names(self) -> List[str]:
        ret = []
        for i in self.rust_vars.values():
            if i.parent is not None and (
                i.parent.name == "input" or i.parent.name == "output"
            ):
                continue
            ret.append(i.name)
        return ret

    def gen_init_localvar(self) -> List[str]:
        ret = []
        for i in self.rust_vars.values():
            if i.parent is not None and (
                i.parent.name == "input" or i.parent.name == "output"
            ):
                continue
            ret.append(i.gen_init_localvar())
        return ret

    def gen_init_tempvar(self) -> List[str]:
        ret = []
        for i in self.temp_vars.values():
            ret.append(i.gen_init_localvar())
        return ret

    def gen_struct_declaration(self) -> List[str]:
        ret = []
        for i in self.rust_vars.values():
            if i.parent is not None and (
                i.parent.name == "input" or i.parent.name == "output"
            ):
                continue
            ret.append(i.gen_struct_declaration())
        return ret

    def gen_global_function_includes(self) -> str:
        prefix = "use crate::engine::{"
        middle = ""
        for k, v in self.global_func.items():
            name = v.name
            middle += f"{name},"
        suffix = "};"
        return prefix + middle + suffix

    def empty(self) -> bool:
        return len(self._temp_code) == 0

    def push_code(self, code: str):
        self._temp_code.append(code)

    def pop_code(self) -> str:
        assert not self.empty()
        return self._temp_code.pop()

    @property
    def temp_vars(self) -> Dict[str, BackendVariable]:
        return self._temp_vars

    @temp_vars.setter
    def temp_vars(self, value: Dict[str, BackendVariable]):
        self._temp_vars = value

    @property
    def def_code(self) -> List[str]:
        return self._def_code

    @def_code.setter
    def def_code(self, value: List[str]):
        self._def_code = value

    @property
    def init_code(self) -> List[str]:
        return self._init_code

    @init_code.setter
    def init_code(self, value: List[str]):
        self._init_code = value

    @property
    def process_code(self) -> List[str]:
        return self._process_code

    @process_code.setter
    def process_code(self, value: List[str]):
        self._process_code = value

    @property
    def tables(self) -> Dict[str, Table]:
        return self._tables

    @tables.setter
    def tables(self, value: Dict[str, Table]):
        self._tables = value

    @property
    def sql_vars(self) -> Dict[str, SQLVariable]:
        return self._sql_vars

    @sql_vars.setter
    def sql_vars(self, value: Dict[str, SQLVariable]):
        self._sql_vars = value

    @property
    def rust_vars(self) -> Dict[str, BackendVariable]:
        return self._rust_vars

    @rust_vars.setter
    def rust_vars(self, value: Dict[str, BackendVariable]):
        self._rust_vars = value
