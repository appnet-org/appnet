/*
  Here we assume compress is a function that takes a RPC and return a compressed RPC.
  We also extend the aggregator grammar to allow it returns a Table, rather than a single value.
  Note that in that case, output type is no longer RPC, but bytes.
*/
INSERT INTO output
SELECT compress(*) from input;

