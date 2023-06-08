from compiler import *

compiler = ADNCompiler(verbose=False)


fault_sqls = [
"""SET probability = 0.2""",
"""
CREATE TABLE output AS 
SELECT * FROM input WHERE random() < probability;
"""]

for sql in fault_sqls:
    # Parse the SQL statement
    generated_code = compiler.transform(sql)
    print(generated_code)
    

logging_sqls = ["""
CREATE TABLE rpc_events (
  timestamp TIMESTAMP,
  event_type VARCHAR(50),
  source VARCHAR(50),
  destination VARCHAR(50),
  rpc VARCHAR(50)
);
""",
"""
INSERT INTO rpc_events (timestamp, type, source, destination, rpc) 
SELECT CURRENT_TIMESTAMP, event_type, src, dst, rpc
FROM input;
""",
"""
CREATE TABLE output AS
SELECT * FROM input; 
"""]

for sql in logging_sqls:
    generated_code = compiler.transform(sql)
    print(generated_code)

acl_sqls = ["""
CREATE TABLE acl (
  name VARCHAR(255),
  permission VARCHAR(2)
);
""",
"""
INSERT INTO acl (permission, name) VALUES
('N', 'Apple'),
('Y', 'Banana'),
""",
"""
CREATE TABLE output AS
SELECT * FROM input JOIN acl ON input.name = acl.name
WHERE acl.permission = 'Y';
"""]

for sql in acl_sqls:
    generated_code = compiler.transform(sql)
    print(generated_code)