SQL_TYPE_TO_RUST_TYPE = {
    "TIMESTAMP":   "DateTime<Utc>",
    "VARCHAR":     "String",
    "INTEGER":     "i32",
    "FLOAT":   "f32",
}


def generate_rust_code(node):
    if node.data == 'start':
        return generate_rust_code(node.children[0]) 
    elif node.data == "statement":
        return generate_rust_code(node.children[0])
    elif node.data == "set_statement":
        return handle_set_statement(node.children[0])
    elif node.data == "create_table_statement":
        return handle_create_table_statement(node)

def handle_set_statement(node):
    variable_name = node.children[0].children[0].value
    value = node.children[1].children[0].value
    rust_code = f"let {variable_name} = {value};"
    return rust_code


def handle_create_table_statement(node):
    # print(node)
    table_name = node.children[0].children[0].value
    if table_name == "output":
        raise ValueError("Table name 'output' is reserved")
    vec_name = "table_" + table_name
    struct_name = "struct_" + table_name
    table = {
        "name": "self." + vec_name,
        "type": "Vec",
        "struct": {
            "name": struct_name,
            "fields": []
        },
    }

    rust_struct = f"pub struct {struct_name} {{\n"
    for column in node.children[1:]:
        print(column)