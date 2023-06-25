from codegen.helper import *
from codegen.snippet import *

def compile_sql_to_rust(ast, ctx):
    if ast["type"] == "CreateTableAsStatement":
        return handle_create_table_as_statement(ast, ctx)
    elif ast["type"] == "CreateTableAsSelect":
        if ast["select"]["type"] == "SelectWhereStatement":
            select_statement = handle_select_where_statement(ast["select"], ctx)
            return f"let {ast['table']}: Vec<_> = {select_statement};"
        elif ast["select"]["type"] == "SelectJoinStatement":
            select_statement = handle_select_join_statement(ast["select"], ctx)
            return f"let {ast['table']}: Vec<_> = {select_statement};"
    elif ast["type"] == "CreateTableStatement":
        return handle_create_table_statement(ast, ctx)
    elif ast["type"] == "InsertStatement":
        return handle_insert_statement(ast, ctx)
    elif ast["type"] == "SetStatement":
        return handle_set_statement(ast, ctx)
    else:
        print(ast)
        raise ValueError("Unsupported SQL statement")

def handle_create_table_statement(ast, ctx):
    table_name = ast["table_name"]
    if table_name == "output":
        raise ValueError("Table name 'output' is reserved")
    if table_name.endswith("_file"):
        ret = generate_create_for_file(ast, ctx, table_name)
    else:
        ret = generate_create_for_vec(ast, ctx, table_name)
    return ret
 
def handle_insert_statement(node, ctx):
    table_name = node["table_name"]
    table = ctx["tables"].get(table_name)
    if table is None:
        raise ValueError("Table does not exist")
    vec_name = table["name"]
    columns = ', '.join(node["columns"])
    value = node["values"][0]
    if type(value) != list and value["type"] == "SelectStatement":
        select = value
        select["to"] = table_name
        select_statement = handle_select_statement(select, ctx)
        rust_code = f"for event in {select_statement} {{"
        if table_name.endswith("file"):
            file_name = table["file_field"]
            rust_code += f"write!(self.{file_name}, \"{{}}\", event);"
        else:
            rust_code += f"{vec_name}.push(event);"
        rust_code += f"}}"
        return rust_code
    else:
        codes = ""
        struct_name = table["struct"]["name"]
        fields = table["struct"]["fields"]
        fields = [i["name"] for i in fields]
        for value in node["values"]:
            values = ""
            for k, v in zip(fields, value):
                v = v.replace("'", "")
                values += f"{k}: \"{v}\".to_string(), "
            codes += f"{vec_name}.push({struct_name} {{{values[:-2]}}});"
        return codes

def handle_select_statement(node, ctx):
    table_from = node["from"]
    if ctx["tables"].get(table_from) is None:
        raise ValueError("Table does not exist")
    table_from = ctx["tables"][table_from]
    table_from_name = table_from["name"]
    if len(node["columns"]) == 1 and node["columns"][0] == "*":
        columns = [i["name"] for i in table_from["struct"]["fields"]]
    else:
        columns = node["columns"]
    if table_from_name == "input":
        columns = [input_mapping(i) for i in columns]
        columns = ', '.join(columns)
    else:
        columns = [f"req.{i}.clone()" for i in columns]
        columns = ', '.join(columns).replace("req.CURRENT_TIMESTAMP.clone()", "Utc::now()")
    if node.get("to") is not None:
        table_to = node["to"]
        if ctx["tables"].get(table_to) is None:
            raise ValueError("Table does not exist")
        table_to = ctx["tables"][table_to]
        struct = table_to["struct"]["name"]
    else:
        struct = table_from["struct"]["name"]
        
    return f"{table_from_name}.iter().map(|req| {struct}::new({columns})).collect::<Vec<_>>()"

def handle_create_table_as_statement(node, ctx):
    new_table = node["table_name"]
    if new_table != "output":
        raise NotImplementedError("Currently only output table is supported")
    select_statement = handle_select_statement(node["select"], ctx)
    return f"let {new_table}: Vec<_> = {select_statement};"

def handle_select_join_statement(node, ctx):
    join_condition = handle_binary_expression(node["join"]["condition"], ctx)
    where_condition = handle_binary_expression(node["where"], ctx)
    join_table_name = node["join"]["table_name"] 
    from_table_name = node["from"]
    if ctx["tables"].get(join_table_name) is None:
        raise ValueError("Table does not exist")
    if ctx["tables"].get(from_table_name) is None:
        raise ValueError("Table does not exist")
    join_vec_name = ctx["tables"][join_table_name]["name"]
    from_vec_name = ctx["tables"][from_table_name]["name"]
    return f"iproduct!({from_vec_name}.iter(), {join_vec_name}.iter()).filter(|&({from_table_name}, {join_table_name})| {join_condition} && {where_condition}).map(|(l, _)| l.clone()).collect()"

def handle_binary_expression(node, ctx):
    left = node["left"]["name"] if node["left"]["data_type"] == "Column" else node["left"]["value"]
    right = node["right"]["name"] if node["right"]["data_type"] == "Column" else node["right"]["value"]
    op = node["operator"]
    if op == "=":
        op = "=="
    return f"{left} {op} {right}"

def handle_set_statement(node, ctx):
    variable_name = node["variable"].replace('@', '')
    ctx["vars"][variable_name] = {
        'name': "var_" + variable_name,
        'value': node["value"]
    }
    variable_name = ctx["vars"][variable_name]["name"]
    rust_code = f"let {variable_name} = {node['value']};"
    return rust_code

def handle_select_where_statement(node, ctx):
    where_condition = handle_where_binary_expression(node["where"], ctx)
    return f"{node['from']}.iter().filter(|&item| {where_condition}).cloned().collect()"

def handle_where_binary_expression(node, ctx):
    left = handle_function(node["left"], ctx) if node["left"]["data_type"] == "Function" else node["left"]["name"]
    right = node["right"]["name"].replace('@', '')
    if ctx["vars"].get(right) is None:
        raise ValueError("Variable does not exist")
    right = ctx["vars"][right]["name"]
    op = node["operator"]
    if op == '=':
        op = "=="
    return f"{left} {op} {right}"

def handle_function(node, ctx):
    if node["name"] == "random":
        return "rand::random::<f32>()"
    else:
        raise ValueError("Unsupported function")
    
    
def init_ctx():
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
                    ]
                }     
            },
            "output": {
                "name": "output",
                "type": "Vec",
                 "struct": {
                    "name": "RpcMessageTx",
                    "fields": [
                        {"name": "meta_buf_ptr", "type": "MetaBufferPtr"},
                        {"name": "addr_backend", "type": "usize"},
                    ]
                } 
            }
        },
        "vars": {
            
        }
    }