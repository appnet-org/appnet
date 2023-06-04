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

def begin_sep(sec):
    return f"\n///@@ BEG_OF {sec} @@\n"

def end_sep(sec):
    return f"\n///@@ END_OF {sec} @@\n"

def handle_create_table_statement(node):
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

    columns = node.children[1:]
    rust_struct = f"pub struct {struct_name} {{\n"
    for column in columns:
        name = column.children[0].children[0].value
        sql_type = column.children[1].children[0].value
        rust_type = SQL_TYPE_TO_RUST_TYPE[sql_type]
        table["struct"]["fields"].append({"name": name, "type": rust_type})
        rust_struct += f"    pub {name}: {rust_type},\n"
    rust_struct += "}\n"
    
    rust_impl = f"impl {struct_name} {{\n"
    rust_impl += f"     pub fn new("
    for column, idx in zip(columns, range(len(columns))):
        name = column.children[0].children[0].value
        sql_type = column.children[1].children[0].value
        rust_impl += f"{name}: {SQL_TYPE_TO_RUST_TYPE[sql_type]}"
        if idx != len(columns) - 1:
            rust_impl += ", "
    rust_impl += f") -> {struct_name} {{\n"
    
    rust_impl += f"         {struct_name} {{\n"
    for column in columns:
        name = column.children[0].children[0].value
        sql_type = column.children[1].children[0].value
        rust_impl += f"             {name}: {sql_type},\n"
    rust_impl += f"         }}\n"
    rust_impl += f"     }}\n"
    rust_impl += f"}}\n"
    
    rust_vec = begin_sep("init") + f"self.{vec_name} = Vec::new();" + end_sep("init")

    rust_internal = begin_sep("internal") + f"pub {vec_name}: Vec<{struct_name}>," + end_sep("internal")
    return begin_sep("declaration") + rust_struct + "\n" + rust_impl + "\n" + end_sep("declaration") + "\n" + rust_vec + "\n" + rust_internal + "\n" + begin_sep("process")
