-- Logging

/* 
Internal state: 
    rpc_events: A table to store rpc events
*/
CREATE TABLE rpc_events (
  timestamp TIMESTAMP,
  type VARCHAR(50),
  source VARCHAR(50),
  destination VARCHAR(50),
  rpc VARCHAR(50)
);


/*
  Processing Logic:
  1. Insert an event for each RPC
  2. Forward all RPCs
*/
INSERT INTO rpc_events (timestamp, type, source, destination, rpc) 
SELECT CURRENT_TIMESTAMP, type, src, dst, values
FROM input;

CREATE TABLE output AS
SELECT * from input; 