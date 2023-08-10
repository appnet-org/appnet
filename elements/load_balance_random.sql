-- Random Load Balancer
/*
We assume that by changing the dst field in RPC.meta, we can change the destination of the RPC.
We assume the layout of an RPC is like (meta.src, meta.dst, meta.type, meta.size, payload).
We assume a special reducer random_reduce  that takes a list of objects and return a random one.
*/
-- init
CREATE TABLE dsts (
  dst VARCHAR(255)
);
INSERT INTO dsts (dst) VALUES ('A') ('B') ('C');
-- processing logic


INSERT INTO output 
SELECT * FROM input;

UPDATE output SET meta_dst = SELECT random_reduce(dst) FROM dsts1;