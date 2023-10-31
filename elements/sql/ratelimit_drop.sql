SET last_ts = CUR_TS();
SET tokens = 5;
SET token_per_sec = 5;

--processing--

SET tokens = tokens + TIME_DIFF(CUR_TS(), last_ts) * token_per_sec;
SET last_ts = CUR_TS();
SET limit = MIN(SELECT COUNT(*) FROM input, tokens);
SET tokens = tokens - limit;
INSERT INTO output SELECT * FROM input LIMIT limit;


