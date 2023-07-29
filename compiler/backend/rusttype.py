from __future__ import annotations

import copy
from enum import Enum
from typing import List, Optional

from backend.abstract import BackendType, BackendVariable
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

    def __init__(self, name: str, init_val: Optional[str] = None):
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
        return (
            f"struct {self.name} {{\n"
            + "\n".join([f"    {i}: {j}," for i, j in self.fields])
            + "\n}"
        )

    def __iter__(self):
        return iter(self.fields)

    # all pub by default
    def gen_definition(self) -> str:
        return (
            f"pub struct {self.name} {{\n"
            + "\n".join([f"    pub {i}: {j.name}," for i, j in self.fields])
            + "\n}"
        )

    def gen_copy_constructor(self) -> str:
        return (
            f"impl {self.name} {{\n"
            + f"    pub fn new({', '.join([f'{i}: {j.name}' for i, j in self.fields])}) -> {self.name} {{\n"
            + f"        {self.name} {{\n"
            + "\n".join([f"            {i}: {i}," for i, j in self.fields])
            + "\n        }\n    }\n}\n"
        )

    def gen_trait_display(self) -> str:
        ret = (
            f"impl fmt::Display for {self.name} {{\n"
            + f"    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {{\n"
        )
        for i, j in self.fields:
            ret += f'        write!(f, "{{}}", self.{i});\n'
        ret += '        write!(f, "\\n")\n'
        ret += "    }\n"
        ret += "}\n"
        return ret


class RustFunctionType(RustType):
    def __init__(self, name: str, args: List[RustType], ret: RustType, definition: str):
        super().__init__(name)
        self.args = args
        self.ret = ret
        self.definition = definition

    def __str__(self) -> str:
        return f"{self.name}({', '.join([str(i) for i in self.args])}) -> {self.ret}"

    def gen_def(self) -> str:
        return self.definition

    def gen_call(self, args: Optional[List[str]] = []) -> str:
        return f"{self.name}({', '.join(args)})"


class RustVariable(BackendVariable):
    def __init__(
        self,
        name: str,
        rust_type: RustType,
        mut: bool,
        init: Optional[str] = None,
        parent: Optional[SQLVariable] = None,
    ) -> None:
        self.name = name
        self.type = rust_type
        self.mut = mut
        if init is None:
            self.init = self.type.gen_init()
        else:
            self.init = init
        self.parent = parent

    def __str__(self) -> str:
        return f"{'mut ' if self.mut else ''}{self.name}: {self.type}"

    def gen_init_localvar(self) -> str:
        return f"let mut {self.name} = {self.init};"

    def gen_init_self(self) -> str:
        return f"self.{self.name} = {self.init};"

    def gen_struct_declaration(self) -> str:
        return f"{self.name}: {self.type.name}"


RustGlobalFunctions = {
    "cur_ts": RustFunctionType(
        "Gen_current_timestamp",
        [],
        RustBasicType("Instant"),
        "pub fn Gen_current_timestamp() -> Instant { Instant::now() }",
    ),
    "time_diff": RustFunctionType(
        "Gen_time_difference",
        [RustBasicType("Instant"), RustBasicType("Instant")],
        RustBasicType("f32"),
        "pub fn Gen_time_difference(a: Instant, b: Instant) -> f32 {(a - b).as_secs_f64() as f32}",
    ),
    "random_f64": RustFunctionType(
        "Gen_random_f64",
        [],
        RustBasicType("f64"),
        "pub fn Gen_random_f64() -> f64 { rand::random::<f64>() }",
    ),
    "min": RustFunctionType(
        "Gen_min",
        [RustBasicType("u64"), RustBasicType("u64")],
        RustBasicType("u32"),
        "pub fn Gen_min(a: u32, b: f32) -> u32 { (a as f32).min(b) as u32}",
    ),
}


tx_struct = RustStructType(
    "RpcMessageTx",
    [
        ("meta_buf_ptr", RustStructType("MetaBufferPtr", [])),
        ("addr_backend", RustBasicType("usize")),
    ],
)

# rx_struct = RustStructType("RpcMessageRx", [("meta_buf_ptr", RustStructType("MetaBufferPtr", [])), ("addr_backend", RustBasicType("usize"))])
