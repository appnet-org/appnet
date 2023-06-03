from compiler import *

compiler = ADNCompiler()


fault_sqls = [
"""
CREATE TABLE acl (
   name VARCHAR(255),
   permission VARCHAR(2)
);
""",
"""SET probability = 0.2""",
"""
CREATE TABLE output AS 
SELECT * FROM input WHERE random() < probability;
"""]

for sql in fault_sqls:
    # Parse the SQL statement
    generated_code = compiler.compile(sql)
    break
    # print(generated_code.pretty())   
    # Access and process the parsed result as desired
    # print(parsed_sql.pretty())
    # print(parsed_sql.children[0].children[0].children[0])
    # for subtree in parsed_sql.iter_subtrees_topdown():
    #     print(subtree.data, subtree.children)
    

# logging_sqls = ["""
# CREATE TABLE rpc_events (
#   timestamp TIMESTAMP,
#   event_type VARCHAR(50),
#   source VARCHAR(50),
#   destination VARCHAR(50),
#   rpc VARCHAR(50)
# );
# """,
# """
# INSERT INTO rpc_events (timestamp, type, source, destination, rpc) 
# SELECT CURRENT_TIMESTAMP, event_type, src, dst, rpc
# FROM input;
# """,
# """
# CREATE TABLE output AS
# SELECT * FROM input; 
# """]

# for sql in logging_sqls:
#     # Parse the SQL statement
#     parsed_sql = sql_parser.parse(sql)

#     # Access and process the parsed result as desired
#     print(parsed_sql.pretty())

# acl_sqls = ["""
# CREATE TABLE acl (
#   name VARCHAR(255),
#   permission VARCHAR(2)
# );
# """,
# """
# INSERT INTO acl (permission, name) VALUES
# ('N', 'Apple'),
# ('Y', 'Banana'),
# """,
# """
# CREATE TABLE output AS
# SELECT * FROM input JOIN acl ON input.name = acl.name
# WHERE acl.permission = "Y";
# """]

# for sql in acl_sqls:
#     # Parse the SQL statement
#     parsed_sql = sql_parser.parse(sql)

#     # Access and process the parsed result as desired
#     print(parsed_sql.pretty())