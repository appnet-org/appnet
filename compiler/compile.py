def compile_sql_to_rust(ast):
    if ast["type"] == "CreateTableAsStatement":
        return handle_create_table_as_statement(ast)
    elif ast["type"] == "CreateTableAsSelect":
        if ast["select"]["type"] == "SelectWhereStatement":
            select_statement = handle_select_where_statement(ast["select"])
            return f"let {ast['table']}: Vec<_> = {select_statement};"
        elif ast["select"]["type"] == "SelectJoinStatement":
            select_statement = handle_select_join_statement(ast["select"])
            return f"let {ast['table']}: Vec<_> = {select_statement};"
    elif ast["type"] == "CreateTableStatement":
        return handle_create_table_statement(ast)
    elif ast["type"] == "InsertStatement":
        return handle_insert_statement(ast)
    elif ast["type"] == "SetStatement":
        return handle_set_statement(ast)
    else:
        raise ValueError("Unsupported SQL statement")

def type_mapping(sql_type):
    if sql_type == "TIMESTAMP":
        return "DateTime<Utc>"
    elif sql_type == "VARCHAR":
        return "String"
    else:
        raise ValueError("Unknown type")

def handle_create_table_statement(ast):
    table_name = ast["table"]
    rust_struct = f"pub struct {table_name} {{\n"
    for column in ast["columns"]:
        rust_type = type_mapping(column["type"])
        rust_struct += f"    pub {column['name']}: {rust_type},\n"
    rust_struct += "}\n"

    rust_vec = f"let {table_name}: Vec<{table_name}> = Vec::new();"

    return rust_struct + "\n" + rust_vec

def handle_insert_statement(node):
    table = node["table"]
    columns = ', '.join(node["columns"])
    if "select" in node:
        select_statement = handle_select_statement(node["select"])
        return f"for event in {select_statement} {{ {table}.push(event); }}"
    else:
        # values = ', '.join(
        #     f"({', '.join(repr(val) for val in row.values())})"
        #     for row in node["values"]
        # )
        values = ""
        for value in node["values"]:
            # print(type(value))
            for k, v in value.items():
                values += f"{k}: '{v}', "

        return f"{table}.push(acl {{{values[:-2]}}});"

def handle_select_statement(node):
    table = node["from"]
    columns = ', '.join(node["columns"]).replace("CURRENT_TIMESTAMP", "Utc::now()")
    return f"{table}.iter().map(|req| RpcEvent::new({columns})).collect::<Vec<_>>()"

def handle_create_table_as_statement(node):
    new_table = node["table"]
    select_statement = handle_select_statement(node["select"])
    return f"let {new_table}: Vec<_> = {select_statement};"

def handle_select_join_statement(node):
    join_condition = handle_binary_expression(node["join"]["condition"])
    where_condition = handle_binary_expression(node["where"])
    return f"iproduct!({node['from']}.iter(), {node['join']['table']}.iter()) .filter(|&(input, acl)| {join_condition} && {where_condition}) .map(|(input, _)| input.clone()) .collect()"

def handle_binary_expression(node):
    return f"{node['left']} {node['operator']} {node['right']}"

def handle_set_statement(node):
    variable_name = node["variable"].replace('@', '') + "_var"
    rust_code = f"let {variable_name} = {node['value']};"
    return rust_code

def handle_select_where_statement(node):
    where_condition = handle_where_binary_expression(node["where"])
    return f"{node['from']}.iter().filter(|&item| {where_condition}).cloned().collect()"

def handle_where_binary_expression(node):
    left = handle_function(node["left"]) if node["left"]["type"] == "Function" else node["left"]["name"]
    right = node["right"]["name"].replace('@', '')
    return f"{left} {node['operator']} {right}"

def handle_function(node):
    if node["name"] == "random":
        return "rand::random::<f32>()"
    else:
        raise ValueError("Unsupported function")