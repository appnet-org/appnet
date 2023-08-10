/*
refer to load_balance_random.sql
We assume at(int x) returns a function that takes a list of objects and return the object at the given x. 
We assume mod(int x) returns a function that takes an int and return the remainder of the int divided by x.
*/
-- init --
CREATE TABLE dsts (
  dst VARCHAR(255)
);
INSERT INTO dsts (dst) VALUES ('A') ('B') ('C');
SET dst_id = 0;
SET dsts_size = SELECT count(*) FROM dsts;
-- processing logic --
INSERT INTO output 
SELECT * FROM INPUT;

UPDATE output SET meta_dst = SELECT at(dst_id)(*) FROM dsts1 ORDER BY dst_id ASC;

SET dst_id = mod(dsts_size)(dst_id + 1);

