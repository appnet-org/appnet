from backend.rusttype import *
from codegen.context import *
from codegen.helper import *
from codegen.snippet import *
from protobuf.protobuf import HelloProto
from tree.node import Node


def visit_root(node, ctx: Context):
    for i in node:
        try:
            visit_single_statement(i, ctx)
        except ValueError as e:
            print("Error in SQL statement: ", e)
            print(i)
            exit()


def visit_single_statement(node, ctx: Context):
    # print("visit_single_statement")
    # print(ast)
    if node["type"] == "CreateTableAsStatement":
        handle_create_table_as_statement(node, ctx)
    elif node["type"] == "SelectStatement":
        if node.get("join") is not None:
            handle_select_join_statement(node, ctx)
        elif node.get("where") is not None:
            handle_select_where_statement(node, ctx)
        else:
            handle_select_simple_statement(node, ctx)
    elif node["type"] == "CreateTableStatement":
        handle_create_table_statement(node, ctx)
    elif node["type"] == "InsertStatement":
        handle_insert_statement(node, ctx)
    elif node["type"] == "SetStatement":
        handle_set_statement(node, ctx)
    else:
        raise ValueError("Unsupported SQL statement", node["type"])


def handle_create_table_statement(node, ctx: Context) -> None:
    table_name = node["table_name"]
    if table_name == "output":
        raise ValueError("Output table should be created by create table as statement")
    if table_name.endswith("_file"):
        generate_create_for_file(node, ctx, table_name)
    else:
        generate_create_for_vec(node, ctx, table_name)


def handle_insert_statement(node, ctx: Context) -> None:
    table_name = node["table_name"]
    table = ctx.tables.get(table_name)
    if table is None:
        raise ValueError("Table does not exist")
    var_name = ctx.rust_vars[table_name].name
    columns = ", ".join(node["columns"])
    value = node["values"][0]
    if type(value) != list and value["type"] == "SelectStatement":
        select = value
        select["to"] = table_name
        handle_select_simple_statement(select, ctx)
        select_statement = ctx.pop_code()

        rust_code = f"for event in {select_statement} {{"
        if table_name.endswith("file"):
            rust_code += f'write!(self.{var_name}, "{{}}", event);'
        else:
            rust_code += f"{var_name}.push(event);"
        rust_code += f"}}"
    else:
        codes = ""
        struct_name = table["struct"]["name"]
        fields = table["struct"]["fields"]
        fields = [i["name"] for i in fields]
        for value in node["values"]:
            values = ""
            for k, v in zip(fields, value):
                if v["data_type"] == "string":
                    v = v["value"].replace("'", "")
                values += f'{k}: "{v}".to_string(), '
            codes += f"{var_name}.push({struct_name} {{{values[:-2]}}})\n"
        rust_code = codes
    ctx.push_code(rust_code)


def handle_select_simple_statement(node, ctx: Context) -> None:
    table_from = node["from"]
    if ctx.tables.get(table_from) is None:
        raise ValueError("Table does not exist")
    table_from = ctx.tables[table_from]
    table_from_name = table_from.name

    if len(node["columns"]) == 1 and node["columns"][0] == "*":
        columns = [i.cname for i in table_from.columns]
    else:
        columns = node["columns"]

    if table_from_name == "input" and ctx.is_forward:
        columns = [i for i, _ in table_from.struct.fields]
        columns = [f"req.{i}.clone()" for i in columns]
        columns = ", ".join(columns)
    elif table_from_name == "input":
        # TODO test protobuf
        columns = [input_mapping(i) for i in columns]
        columns = ", ".join(columns)
    else:
        columns = [f"req.{i.cname}.clone()" for i in columns]
        columns = ", ".join(columns).replace(
            "req.CURRENT_TIMESTAMP.clone()", "Utc::now()"
        )

    if node.get("to") is not None:
        table_to_name = node["to"]
        if ctx.tables.get(table_to_name) is None:
            raise ValueError("Table does not exist")
        table_to = ctx.tables[table_to_name]
        struct = table_to.struct
    else:
        struct = table_from.struct

    if ctx.is_forward == True:
        code = f"{table_from_name}.iter().map(|req| RpcMessageGeneral::TxMessage(EngineTxMessage::RpcMessage({struct.name}::new({columns})))).collect::<Vec<_>>()"
    else:
        code = f"{table_from_name}.iter().map(|req| {struct.name}::new({columns})).collect::<Vec<_>>()"
    ctx.push_code(code)


def handle_create_table_as_statement(node, ctx: Context) -> None:
    new_table = node["table_name"]
    if new_table != "output":
        raise NotImplementedError("Currently only output table is supported")
    select = node["select"]
    if new_table == "output":
        ctx.is_forward = True

    visit_single_statement(select, ctx)
    select_statement = ctx.pop_code()

    if new_table == "output" and ctx.is_forward == True:
        ctx.is_forward = False

    if select["type"] == "SelectJoinStatement":
        code = f"let {new_table}: Vec<_> = {select_statement};"
    elif select["type"] == "SelectWhereStatement":
        code = f"let {new_table}: Vec<_> = {select_statement};"
    elif select["type"] == "SelectStatement":
        code = f"let {new_table}: Vec<_> = {select_statement};"
    else:
        raise ValueError("Unsupported select statement type")

    ctx.push_code(code)


def handle_select_join_statement(node, ctx):
    join_condition = handle_binary_expression(node["join"], ctx)
    where_condition = handle_binary_expression(node["where"], ctx)
    join_table_name = node["join"]["table"]
    from_table_name = node["from"]
    from_table_name = ctx["tables"][from_table_name]["name"]
    if ctx["tables"].get(join_table_name) is None:
        raise ValueError("Table does not exist")
    if ctx["tables"].get(from_table_name) is None:
        raise ValueError("Table does not exist")
    join_vec_name = ctx["tables"][join_table_name]["name"]
    from_vec_name = ctx["tables"][from_table_name]["name"]
    if from_vec_name != "input" and from_vec_name != "output":
        from_vec_name = f"self.{from_vec_name}"
    if join_vec_name != "input" and join_vec_name != "output":
        join_vec_name = f"self.{join_vec_name}"
    func = generate_join_filter_function(
        join_condition, where_condition, from_table_name, join_table_name, ctx["proto"]
    )
    # gen_filter_function(from_table_name, join_table_name, join_condition)
    code = f"iproduct!({from_vec_name}.iter(), {join_vec_name}.iter()).map({func}).collect()"
    ctx["code"].append(code)


def handle_select_where_statement(node, ctx):
    where_condition = handle_binary_expression(node["where"], ctx)
    func = generate_where_filter_function(where_condition, ctx["proto"])
    code = f"{node['from']}.iter().map({func}).collect()"
    ctx["code"].append(code)


def handle_expression(node, ctx):
    if node["data_type"] == "Column":
        return node["table_name"], node["column_name"]
    elif node["data_type"] == "Literal":
        return "Literal", node["value"]
    elif node["data_type"] == "Function":
        return "Function", handle_function(node, ctx)
    elif node["data_type"] == "Variable":
        name = node["name"]
        if ctx["vars"].get(name) is None:
            raise ValueError("Variable does not exist")
        name = ctx["vars"][name]["name"]
        return "Variable", name


def handle_binary_expression(node, ctx):
    if node["type"] == "BinaryExpression":
        lt, lc = handle_expression(node["left"], ctx)
        rt, rc = handle_expression(node["right"], ctx)
        op = node["operator"]
    elif node["type"] == "JoinOn":
        cond = node["condition"]
        lt, lc = handle_expression(cond["left"], ctx)
        rt, rc = handle_expression(cond["right"], ctx)
        op = cond["operator"]
        if op == "=":
            op = "=="
    if rt == "Literal":
        rc = rc.replace("'", '"')
    if lt == "Literal":
        lc = lc.replace("'", '"')
    return {"lt": lt, "lc": lc, "rt": rt, "rc": rc, "op": op}


def handle_set_statement(node, ctx):
    variable_name = node["variable"].replace("@", "")
    ctx["vars"][variable_name] = {
        "name": "var_" + variable_name,
        "value": node["value"],
    }
    val = node["value"]
    var_type = "i32"
    if "'" in val:
        var_type = "String"
    elif "." in val:
        var_type = "f32"
    else:
        var_type = "i32"
    variable_name = ctx["vars"][variable_name]["name"]
    rust_code = begin_sep("type") + var_type + end_sep("type")
    rust_code += begin_sep("name") + variable_name + end_sep("name")
    rust_code += begin_sep("init") + f"{variable_name} = {val}" + end_sep("init")
    ctx["code"].append(rust_code)


def handle_function(node, ctx):
    if node["name"] == "random":
        return "rand::random::<f32>()"
    else:
        raise ValueError("Unsupported function")


def init_ctx() -> Context:
    InputTable = Table(
        "input",
        [
            Column("input", "type", "string"),
            Column("input", "src", "string"),
            Column("input", "dst", "string"),
            Column("input", "payload", "protobuf"),
        ],
        tx_struct,
    )
    OutputTable = Table(
        "output",
        [
            Column("output", "type", "string"),
            Column("output", "src", "string"),
            Column("output", "dst", "string"),
            Column("output", "payload", "protobuf"),
        ],
        tx_struct,
    )
    input_vec = RustVariable(
        "input", RustContainerType("Vec", tx_struct), False, None, InputTable
    )
    output_vec = RustVariable(
        "output", RustContainerType("Vec", tx_struct), True, None, OutputTable
    )
    ret = Context([InputTable, OutputTable], [input_vec, output_vec], HelloProto)
    for _, func in RustGlobalFunctions.items():
        ret.def_code.append(func.gen_def())
    ret.def_code += ret.proto.gen_readonly_def()
    ret.global_func = RustGlobalFunctions
    return ret
    # def init_ctx():
    return {
        "tables": {
            "input": {
                "name": "input",
                "type": "Vec",
                "struct": {
                    "name": "RpcMessageTx",
                    "fields": [
                        {"name": "meta_buf_ptr", "type": "MetaBufferPtr"},
                        {"name": "addr_backend", "type": "usize"},
                    ],
                },
            },
            "output": {
                "name": "output",
                "type": "Vec",
                "struct": {
                    "name": "RpcMessageTx",
                    "fields": [
                        {"name": "meta_buf_ptr", "type": "MetaBufferPtr"},
                        {"name": "addr_backend", "type": "usize"},
                    ],
                },
                "oncreate": False,
            },
        },
        "vars": {},
        "proto": {
            "name": "hello",
            "req_type": "hello::HelloRequest",
            "resp_type": "hello::HelloResponse",
        },
        "code": [],
    }
