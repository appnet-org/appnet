CREATE TABLE rpc_events (
  timestamp TIMESTAMP,
  type VARCHAR(50),
  source VARCHAR(50),
  destination VARCHAR(50),
  rpc VARCHAR(50)
);

CREATE PROCEDURE logging AS 
INSERT INTO rpc_events (timestamp, type, source, destination, rpc) 
SELECT CURRENT_TIMESTAMP, type, src, dst, values
FROM input;

--  Create the output table
CREATE TABLE output AS
SELECT * from input; 