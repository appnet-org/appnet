from typing import Tuple

from backend.rusttype import *
from codegen.context import *
from codegen.helper import *


def trans_col_rust(column) -> Tuple[str, RustType]:
    # print(column[1].sql_type())
    rust_type = type_mapping(column[1].sql_type())
    return (column[0].column_name, rust_type)


def trans_col(table: str, column) -> Column:
    return Column(table, column[0].column_name, column[1].sql_type())


def generate_struct_declaration(struct_name, columns, table):
    rust_struct = f"pub struct {struct_name} {{\n"
    for column in columns:
        rust_type = type_mapping(column["data_type"])
        table["struct"]["fields"].append(
            {"name": column["column_name"], "type": rust_type}
        )
        rust_struct += f"    pub {column['column_name']}: {rust_type},\n"
    rust_struct += "}\n"
    return rust_struct, struct_name


def generate_new(struct_name, columns):
    rust_impl = f"impl {struct_name} {{\n"
    rust_impl += f"     pub fn new("
    for column, idx in zip(columns, range(len(columns))):
        rust_impl += f"{column['column_name']}: {type_mapping(column['data_type'])}"
        if idx != len(columns) - 1:
            rust_impl += ", "
    rust_impl += f") -> {struct_name} {{\n"

    rust_impl += f"         {struct_name} {{\n"
    for column in columns:
        rust_impl += f"             {column['column_name']}: {column['column_name']},\n"
    rust_impl += f"         }}\n"
    rust_impl += f"     }}\n"
    rust_impl += f"}}\n"
    return rust_impl


def generate_create_for_vec(ast, ctx: Context, table_name: str):
    vec_name = "vec_" + table_name
    struct_name = "struct_" + table_name

    # table = {
    #     "name": vec_name,
    #     "type": "Vec",
    #     "struct": {
    #         "name": struct_name,
    #         "fields": []
    #     },
    # }

    rust_struct = RustStructType(
        struct_name, [trans_col_rust(i) for i in ast["columns"]]
    )
    table = Table(table_name, [trans_col(i) for i in ast["columns"]], rust_struct)

    if ctx.tables.get(table_name) is None:
        ctx.tables[table_name] = table
    else:
        raise ValueError("Table already exists")

    # rust_struct, rust_extern = generate_struct_declaration(struct_name, ast["columns"], table)
    # rust_extern = begin_sep("declaration") + rust_extern + end_sep("declaration")
    # rust_impl = generate_new(struct_name, ast["columns"])

    # rust_vec = begin_sep("name") + f"{vec_name}" + end_sep("name")
    # rust_vec += begin_sep("type") + f"{table['type']}<{struct_name}>" + end_sep("type")
    # rust_vec += begin_sep("init") + f"{vec_name} = Vec::new()" + end_sep("init")

    ctx.def_code.append(
        rust_struct.gen_definition() + "\n" + rust_struct.gen_copy_constructor()
    )

    ctx.rust_vars.update(
        {
            table_name: RustVariable(
                vec_name, RustContainerType("Vec", rust_struct), True, None, table
            )
        }
    )
    # return rust_extern + begin_sep("definition") + rust_struct + "\n" + rust_impl + "\n" + end_sep("definition") + "\n" + rust_vec + "\n"


def generate_create_for_file(ast, ctx: Context, table_name: str):
    file_name = "file_" + table_name
    struct_name = "struct_" + table_name
    # table = {
    #     "name": file_name,
    #     "type": "File",
    #     "struct": {
    #         "name": struct_name,
    #         "fields": []
    #     },
    #     "file_field": "log_file",
    # }

    rust_struct = RustStructType(
        struct_name, [trans_col_rust(i) for i in ast["columns"]]
    )
    table = Table(
        table_name, [trans_col(table_name, i) for i in ast["columns"]], rust_struct
    )

    if ctx.tables.get(table_name) is None:
        ctx.tables[table_name] = table
    else:
        raise ValueError("Table already exists")

    # file_field = table["file_field"]

    # rust_struct, rust_extern = generate_struct_declaration(struct_name, ast["columns"], table)
    # rust_extern = begin_sep("declaration") + rust_extern + end_sep("declaration")

    # rust_impl = generate_new(struct_name, ast["columns"]);
    # rust_impl += "\n"

    # rust_impl += f"impl fmt::Display for {struct_name} {{\n"
    # rust_impl += f"     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {{\n"
    # fields = table["struct"]["fields"]
    # for field in fields:
    #     name = field["name"]
    #     if name != file_field:
    #         rust_impl += f"         write!(f, \"{{}},\", self.{name});\n"
    # rust_impl += f"         write!(f, \"\\n\")\n"
    # rust_impl += f"     }}\n"
    # rust_impl += f"}}\n"

    # rust_file = begin_sep("type") + "File" + end_sep("type");
    # rust_file += begin_sep("name") + f"{file_field}" + end_sep("name")
    # rust_file += begin_sep("init") + f"{file_field} = create_log_file()" + end_sep("init")

    ctx.def_code.append(
        rust_struct.gen_definition()
        + "\n"
        + rust_struct.gen_copy_constructor()
        + "\n"
        + rust_struct.gen_trait_display()
    )

    ctx.rust_vars.update(
        {
            table_name: RustVariable(
                file_name, RustBasicType("File"), True, "create_log_file()", table
            )
        }
    )

    # return rust_extern + begin_sep("definition") + rust_struct + "\n" + rust_impl + "\n" + end_sep("definition") + "\n" + rust_file + "\n"


def generate_rpc_fields_getter():
    pass


def decorate_condition(cond, proto_ctx):
    proto = proto_ctx["name"]
    if cond["lt"] == "input":
        lc = cond["lc"]
        if input_mapping(lc) == True:
            left = f"{proto}_request_{lc}_readonly(rpc_message)"
        else:
            raise NotImplementedError("Not implemented")
    elif cond["lt"] == "Literal":
        left = cond["lc"]
    elif cond["lt"] == "Variable":
        left = f"self.{cond['lc']}"
    elif cond["lt"] == "Function":
        left = cond["lc"]
    else:
        left = f"join.{cond['lc']}"

    if cond["rt"] == "input":
        rc = cond["rc"]
        if input_mapping(rc) == True:
            right = f"{proto}_request_{rc}_readonly(rpc_message)"
        else:
            raise NotImplementedError("Not implemented")
    elif cond["rt"] == "Literal":
        right = cond["rc"]
    elif cond["rt"] == "Variable":
        right = f"self.{cond['rc']}"
    elif cond["rt"] == "Function":
        right = cond["rc"]
    else:
        right = f"join.{cond['rc']}"
    return f"{left} {cond['op']} {right}"


def generate_join_filter_function(join_cond, filter_cond, lt, rt, proto_ctx):
    if lt != "input":
        raise ValueError("Only support when left table is input")

    join_cond = decorate_condition(join_cond, proto_ctx)
    filter_cond = decorate_condition(filter_cond, proto_ctx)
    proto = proto_ctx["name"]
    proto_req_type = proto_ctx["req_type"]
    return f"""
|(msg, join)| {{
    let rpc_message = materialize_nocopy(&msg);
    let conn_id = unsafe {{ &*msg.meta_buf_ptr.as_meta_ptr() }}.conn_id;
    let call_id = unsafe {{ &*msg.meta_buf_ptr.as_meta_ptr() }}.call_id;
    let rpc_id = RpcId::new(conn_id, call_id);
    if {join_cond} {{
        if {filter_cond} {{
            let error = EngineRxMessage::Ack(
                rpc_id,
                TransportStatus::Error(unsafe {{
                    NonZeroU32::new_unchecked(403)
                }}),
            );
            RpcMessageGeneral::RxMessage(error)
        }} else {{
            let raw_ptr: *const {proto_req_type} = rpc_message;
            let new_msg = RpcMessageTx {{
                meta_buf_ptr: msg.meta_buf_ptr.clone(),
                addr_backend: raw_ptr.addr(),
            }};
            RpcMessageGeneral::TxMessage(EngineTxMessage::RpcMessage(
                new_msg,
            ))
        }}
    }} else {{
        RpcMessageGeneral::Pass
    }}
}}
"""


def generate_where_filter_function(cond, proto_ctx):
    cond = decorate_condition(cond, proto_ctx)
    proto = proto_ctx["name"]
    proto_req_type = proto_ctx["req_type"]
    return f"""
|msg| {{
    let rpc_message = materialize_nocopy(&msg);
    let conn_id = unsafe {{ &*msg.meta_buf_ptr.as_meta_ptr() }}.conn_id;
    let call_id = unsafe {{ &*msg.meta_buf_ptr.as_meta_ptr() }}.call_id;
    let rpc_id = RpcId::new(conn_id, call_id);
    if {cond} {{
        let error = EngineRxMessage::Ack(
            rpc_id,
            TransportStatus::Error(unsafe {{
                NonZeroU32::new_unchecked(403)
            }}),
        );
        RpcMessageGeneral::RxMessage(error)
    }} else {{
        let raw_ptr: *const {proto_req_type} = rpc_message;
        let new_msg = RpcMessageTx {{
            meta_buf_ptr: msg.meta_buf_ptr.clone(),
            addr_backend: raw_ptr.addr(),
        }};
        RpcMessageGeneral::TxMessage(EngineTxMessage::RpcMessage(
            new_msg,
        ))
    }}
}}
"""
