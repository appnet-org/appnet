import sqlparse

def parse_sql(sql):
    ast = {}
    statement = sqlparse.parse(sql)[0]  
    if statement.get_type() == "CREATE":
        ast = parse_create_table(statement)
    elif statement.get_type() == "SELECT":
        ast = parse_select(statement)
    else:
        raise ValueError("Unsupported SQL statement")
    return ast

def get_table_name(tokens):
    for token in reversed(tokens):
        if token.ttype is None:
            return token.value
    return " "

def parse_create_table(parsed):
    ast = {"type": "CreateTableStatement", "columns": []}
    for token in parsed.tokens:
        # print(token)
        # print(token.ttype)
        if token.ttype is None:
            print(type(token.value))
            if token.value.startswith("("):
                print(token.tokens)
                for subtoken in token.tokens:
                    if subtoken.ttype is sqlparse.tokens.Name:
                        column = {"name": subtoken.value}
                        tlist = list(subtoken.parent.flatten())
                        idx = tlist.index(subtoken)
                        column["type"] = tlist[idx + 2].value
                        column["length"] = parse_length(tlist[idx + 3:])
                        ast["columns"].append(column)
            else:
                ast["table"] = token.value
           
    return ast

def parse_select(statement):
    ast = {"type": "SelectStatement", "columns": [], "from": []}
    for token in statement.tokens:
        if token.ttype is None:
            if token.get_real_name() == "SELECT":
                ast["columns"] = [{"type": "Column", "name": str(name.get_real_name())}
                                  for name in token.get_identifiers()]
            elif token.get_real_name() == "FROM":
                ast["from"] = [{"type": "Table", "name": str(name.get_real_name())}
                               for name in token.get_identifiers()]
    return ast

sql_create = 'CREATE TABLE rpc_events (ts TIMESTAMP, type VARCHAR(50), source VARCHAR(50), destination VARCHAR(50), rpc VARCHAR(50));'
sql_select = 'SELECT name FROM users WHERE id = 1;'

print(parse_sql(sql_create))
# print(parse_sql(sql_select))