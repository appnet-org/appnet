from compile import *
import os

if __name__ == "__main__":
    os.system("rm -f ./generated/*")
    
    logging_asts = [{
    "type": "CreateTableStatement",
    "table": "rpc_events",
    "columns": [
        {"name": "timestamp", "type": "TIMESTAMP"},
        {"name": "event_type", "type": "VARCHAR", "length": 50},
        {"name": "source", "type": "VARCHAR", "length": 50},
        {"name": "destination", "type": "VARCHAR", "length": 50},
        {"name": "rpc", "type": "VARCHAR", "length": 50}
    ]
    },
    {
        "type": "InsertStatement",
        "table": "rpc_events",
        "columns": ["timestamp", "event_type", "source", "destination", "rpc"],
        "select": {
            "type": "SelectStatement",
            "columns": ["CURRENT_TIMESTAMP", "event_type", "source", "destination", "payload"],
            "from": "input"
        }
    },
    {
        "type": "CreateTableAsStatement",
        "table": "output",
        "select": {
            "type": "SelectStatement",
            "columns": ["*"],
            "from": "input"
        }
    }]
    print("Compiling logging statements...")

    ctx = init_ctx()
    for ast in logging_asts:
        rust_code = compile_sql_to_rust(ast, ctx)
        print(rust_code)
        with open("./generated/logging.rs", "a") as f:
            f.write(rust_code + '\n')

    acl_asts = [{
    "type": "CreateTableStatement",
    "table": "acl",
    "columns": [
        {"name": "name", "type": "VARCHAR", "length": 50},
        {"name": "permission", "type": "VARCHAR", "length": 2},
    ]
    },
    {
    "type": "InsertStatement",
    "table": "acl",
    "columns": ["permission", "name"],
    "values": [
     #   {"permission": "N", "name": "Apple"},
        {"permission": "Y", "name": "Banana"}
    ]
    },
    {
    "type": "CreateTableAsSelect",
    "table": "output",
    "select": {
        "type": "SelectJoinStatement",
        "from": "input",
        "join": {
            "type": "JoinOn",
            "table": "acl",
            "condition": {
                "left": {"type": "Column", "name": "input.source"},
                "operator": "=",
                "right": {"type": "Column", "name": "acl.name"}
            }
        },
        "where": {
            "type": "BinaryExpression",
            "left": {"type": "Column", "name": "acl.permission"},
            "operator": "=",
            "right": {"type": "Literal", "value": "\"Y\""}
        }
    }
    }]
    print()
    print("Compiling acl statements...")
    ctx = init_ctx()
    for ast in acl_asts:
        rust_code = compile_sql_to_rust(ast, ctx)
        print(rust_code)
        with open("./generated/acl.rs", "a") as f:
            f.write(rust_code + '\n')

    
    fault_asts = [
    {
    "type": "SetStatement",
    "variable": "@probability",
    "value": "0.2"
    },
    {
    "type": "CreateTableAsSelect",
    "table": "output",
    "select": {
        "type": "SelectWhereStatement",
        "from": "input",
        "where": {
            "type": "BinaryExpression",
            "left": {"type": "Function", "name": "random"},
            "operator": "<",
            "right": {"type": "Variable", "name": "@probability"}
        }
    }
    }]
    print()
    print("Compiling fault statements...")
    ctx = init_ctx()
    for ast in fault_asts:
        rust_code = compile_sql_to_rust(ast, ctx)
        print(rust_code)
        with open("./generated/fault.rs", "a") as f:
            f.write(rust_code + '\n')