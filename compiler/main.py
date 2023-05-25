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
        {"permission": "Y", "name": "Banana"}
    ]
    }]

    for ast in acl_asts:
        rust_code = compile_sql_to_rust(ast)
        print(rust_code)