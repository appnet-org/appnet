import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function
from sqlparse.tokens import Keyword, DML

def parse_sql_to_ast(sqls):
    ast = []
    for sql in sqls:
        stmt = sqlparse.parse(sql)[0]
        if stmt.get_type() == 'CREATE':
            ast.append(parse_create(stmt))
        elif stmt.get_type() == 'INSERT':
            ast.append(parse_insert(stmt))
    
    return ast

def find_identifier(tokens):
    for token in tokens:
        if isinstance(token, Identifier) or isinstance(token, Function):
            return token.value
    return None

def parse_create(stmt):
    tokens = stmt.tokens
    # First extract the table name
    table = find_identifier(tokens)
    
    # if str(tokens[4]).lower() == 'as':
    #     return {
    #         "type": "CreateTableAsStatement",
    #         "table": table,
    #         "select": parse_select(tokens[6])
    #     }
    _, par = stmt.token_next_by(i=sqlparse.sql.Parenthesis)
    columns = parse_columns(par)
    return {
        "type": "CreateTableStatement",
        "table": table,
        "columns": columns
    }

def parse_insert(stmt):
    tokens = stmt.tokens
    print(tokens)


    table = find_identifier(tokens)
    print(table)
    columns = [str(t).strip() for t in tokens[4].tokens[1:-1:2]]
    select = parse_select(tokens[6])
    return {
        "type": "InsertStatement",
        "table": table,
        "columns": columns,
        "select": select
    }

def parse_select(stmt):
    tokens = stmt.tokens
    columns = [str(t).strip() for t in tokens[2].tokens[1:-1:2]]
    from_table = str(tokens[4]).strip()
    return {
        "type": "SelectStatement",
        "columns": columns,
        "from": from_table
    }

def parse_columns(token_list):
    # print(token_list)
    columns = []
    tmp = []
    par_level = 0
    for token in token_list.flatten():
        if token.is_whitespace:
            continue
        elif token.match(sqlparse.tokens.Punctuation, '('):
            par_level += 1
            continue
        if token.match(sqlparse.tokens.Punctuation, ')'):
            if par_level == 0:
                break
            else:
                par_level += 1
        elif token.match(sqlparse.tokens.Punctuation, ','):
            if tmp:
                if len(tmp) == 3 and tmp[1].value.upper() == 'VARCHAR':
                    columns.append({
                        "name": tmp[0].value,
                        "type": tmp[1].value.upper(),
                        "length": int(tmp[2].value)
                    })
                else:
                    columns.append({
                        "name": tmp[0].value,
                        "type": tmp[1].value.upper(),
                    })
            tmp = []
        else:
            tmp.append(token)
    if tmp:
        if len(tmp) == 3 and tmp[1].value.upper() == 'VARCHAR':
            columns.append({
                "name": tmp[0].value,
                "type": tmp[1].value.upper(),
                "length": int(tmp[2].value)
            })
        else:
            columns.append({
                "name": tmp[0].value,
                "type": tmp[1].value.upper(),
            })
    return columns

sqls = ["""
CREATE TABLE rpc_events (
  rpc_timestamp TIMESTAMP,
  event_type VARCHAR(50),
  source VARCHAR(50),
  destination VARCHAR(50),
  rpc VARCHAR(50)
);
""",
"""
INSERT INTO rpc_events (timestamp, event_type, source, destination, rpc) 
SELECT CURRENT_TIMESTAMP, event_type, src, dst, rpc
FROM input;
""",]
# """
# INSERT INTO rpc_events (timestamp, event_type, source, destination, rpc) 
# SELECT CURRENT_TIMESTAMP, event_type, src, dst, rpc
# FROM input;
# """,
# """
# CREATE TABLE output AS
# SELECT * from input; 
# """]
ast = parse_sql_to_ast(sqls)
print(ast)
