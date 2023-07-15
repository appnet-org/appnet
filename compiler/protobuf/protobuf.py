from typing import List


class ProtoMessage:
    """
    Assume that all fields are Bytes
    """

    def __init__(self, name: str, fields: List[str]) -> None:
        self.name = name
        self.fields = fields

    def gen_readonly(self, proto: str):
        ret = []
        for field in self.fields:
            ret.append(
                """
            fn {proto}_{name}_{field}_readonly(req: &{proto}::{name}) -> String {{
            let buf = &req.{field} as &[u8];
            String::from_utf8_lossy(buf).to_string().clone()
        }}""".format(
                    proto=proto, name=self.name, field=field
                )
            )
        return ret


class Proto:
    def __init__(self, name: str, msg: List[ProtoMessage]) -> None:
        self.name = name
        self.msg = msg

    def namespace(self):
        return self.name

    def gen_readonly(self):
        ret = []
        for msg in self.msg:
            ret.append("\n".join(msg.gen_readonly(self.name)))
        return ret


HelloProto = Proto(
    "hello",
    [
        ProtoMessage("HelloRequest", ["name"]),
        ProtoMessage("HelloResponse", ["message"]),
    ],
)
