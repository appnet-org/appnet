def compile_sql_to_rust(ast):
    if ast["type"] == "CreateTableAsStatement":
        return handle_create_table_as_statement(ast)
    elif ast["type"] == "CreateTableStatement":
        return handle_create_table_statement(ast)
    elif ast["type"] == "InsertStatement":
        return handle_insert_statement(ast)
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
        values = handle_select_statement(node["select"])
    else:
        values = ', '.join(
            f"({', '.join(repr(val) for val in row.values())})"
            for row in node["values"]
        )
    return f"{table}.insert(({columns})).values(({values}));"

def handle_select_statement(node):
    table = node["from"]
    columns = ', '.join(node["columns"]).replace("CURRENT_TIMESTAMP", "Utc::now()")
    return f"{table}.select({columns}).load::<({columns})>(&connection).unwrap()"

def handle_create_table_as_statement(node):
    new_table = node["table"]
    select_statement = handle_select_statement(node["select"])
    return f"let {new_table}: Vec<_> = {select_statement};"

