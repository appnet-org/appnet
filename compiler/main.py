from compile import *

if __name__ == "__main__":
    logging_asts = [{
    "type": "CreateTableStatement",
    "table": "rpc_events",
    "columns": [
        {"name": "timestamp", "type": "TIMESTAMP"},
        {"name": "type", "type": "VARCHAR", "length": 50},
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
            "columns": ["CURRENT_TIMESTAMP", "event_type", "source", "destination", "rpc"],
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
    for ast in logging_asts:
        rust_code = compile_sql_to_rust(ast)
        print(rust_code)

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
        {"permission": "N", "name": "Apple"},
        # {"permission": "Y", "name": "Banana"}
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
                "left": "input.name",
                "operator": "=",
                "right": "acl.name"
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
    for ast in acl_asts:
        rust_code = compile_sql_to_rust(ast)
        print(rust_code)

    
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
    for ast in fault_asts:
        rust_code = compile_sql_to_rust(ast)
        print(rust_code)