SET last_ts = CUR_TS();
SET tokens = 5;
SET token_per_sec = 50;

--processing--

SET tokens = tokens + TIME_DIFF(CUR_TS(), last_ts) * token_per_sec;
SET last_ts = CUR_TS();
SET size = SELECT meta_size FROM input LIMIT 1; 
SET limit = MIN((SELECT COUNT(*) FROM input) * size, tokens);
SET tokens = tokens - limit * size;
INSERT INTO output SELECT * FROM input LIMIT limit;


