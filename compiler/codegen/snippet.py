from codegen.helper import *

def generate_struct_declaration(struct_name, columns, table):
    rust_struct = f"pub struct {struct_name} {{\n"
    for column in columns:
        rust_type = type_mapping(column["data_type"])
        table["struct"]["fields"].append({"name": column["column_name"], "type": rust_type})
        rust_struct += f"    pub {column['column_name']}: {rust_type},\n"
    rust_struct += "}\n" 
    return rust_struct

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

def generate_create_for_vec(ast, ctx, table_name):
    vec_name = "table_" + table_name
    struct_name = "struct_" + table_name
    table = {
        "name": vec_name,
        "type": "Vec",
        "struct": {
            "name": struct_name,
            "fields": []
        },
    }
    if ctx["tables"].get(table_name) is None:
        ctx["tables"][table_name] = table
    else:
        raise ValueError("Table already exists")
    
    rust_struct = generate_struct_declaration(struct_name, ast["columns"], table)

    rust_impl = generate_new(struct_name, ast["columns"])
    
    rust_vec = begin_sep("name") + f"{vec_name}" + end_sep("name") 
    rust_vec += begin_sep("type") + f"{table['type']}<{struct_name}>" + end_sep("type")
    rust_vec += begin_sep("init") + f"{vec_name} = Vec::new()" + end_sep("init")

    return begin_sep("declaration") + rust_struct + "\n" + rust_impl + "\n" + end_sep("declaration") + "\n" + rust_vec + "\n" + begin_sep("process")
 
    
def generate_create_for_file(ast, ctx, table_name):
    file_name = "table_" + table_name
    struct_name = "struct_" + table_name
    table = {
        "name": file_name,
        "type": "File",
        "struct": {
            "name": struct_name,
            "fields": []
        },
        "file_field": "log_file",
    }
    if ctx["tables"].get(table_name) is None:
        ctx["tables"][table_name] = table
    else:
        raise ValueError("Table already exists")

    file_field = table["file_field"]

    rust_struct = generate_struct_declaration(struct_name, ast["columns"], table)
    
    rust_impl = generate_new(struct_name, ast["columns"]);
    rust_impl += "\n"
    
    rust_impl += f"impl fmt::Display for {struct_name} {{\n"
    rust_impl += f"     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {{\n"
    fields = table["struct"]["fields"]
    for field in fields:
        name = field["name"]
        if name != file_field:
            rust_impl += f"         write!(f, \"{{}},\", self.{name});\n"
    rust_impl += f"         write!(f, \"\\n\")\n"
    rust_impl += f"     }}\n"
    rust_impl += f"}}\n"
    
    rust_file = begin_sep("type") + "File" + end_sep("type");
    rust_file += begin_sep("name") + f"{file_field}" + end_sep("name")
    rust_file += begin_sep("init") + f"{file_field} = create_log_file()" + end_sep("init") 


    return begin_sep("declaration") + rust_struct + "\n" + rust_impl + "\n" + end_sep("declaration") + "\n" + rust_file + "\n" + begin_sep("process")