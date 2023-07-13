from backend.rusttype import *
from codegen.context import *


def begin_sep(sec):
    return f"\n///@@ BEG_OF {sec} @@\n"


def end_sep(sec):
    return f"\n///@@ END_OF {sec} @@\n"


def to_str_debug(x):
    return f'format!("{{:?}}", {x})'


def to_str(x):
    return f'format!("{{}}", {x})'


def type_mapping(sql_type):
    if sql_type == "TIMESTAMP":
        return RustContainerType("DateTime", RustBasicType("Utc"))
        # return "DateTime<Utc>"
    elif sql_type == "VARCHAR":
        return RustBasicType("String")
    elif sql_type == "FILE":
        return RustBasicType("File")
    else:
        raise ValueError("Unknown type")


def input_mapping(field: Column) -> str:
    if field == "CURRENT_TIMESTAMP":
        return "Utc::now()"
    elif field == "event_type":
        return to_str_debug("meta_ref.msg_type")
    elif field == "src":
        return to_str_debug("meta_ref.conn_id")
    elif field == "dst":
        return to_str_debug("meta_ref.conn_id")
    elif field == "rpc":
        return to_str("req.addr_backend.clone()")
    elif field == "meta_buf_ptr":
        return "req.meta_buf_ptr.clone()"
    elif field == "addr_backend":
        return "req.addr_backend.clone()"
    else:
        return "NOT_IMPLEMENTED"
