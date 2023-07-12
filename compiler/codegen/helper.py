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
        return "DateTime<Utc>"
    elif sql_type == "VARCHAR":
        return "String"
    elif sql_type == "FILE":
        return "File"
    else:
        raise ValueError("Unknown type")


def input_mapping(fields):
    if fields == "CURRENT_TIMESTAMP":
        return "Utc::now()"
    elif fields == "event_type":
        return to_str_debug("meta_ref.msg_type")
    elif fields == "src":
        return to_str_debug("meta_ref.conn_id")
    elif fields == "dst":
        return to_str_debug("meta_ref.conn_id")
    elif fields == "rpc":
        return to_str("req.addr_backend.clone()")
    elif fields == "meta_buf_ptr":
        return "req.meta_buf_ptr.clone()"
    elif fields == "addr_backend":
        return "req.addr_backend.clone()"
    else:
        return True
