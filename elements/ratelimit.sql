/*
  Internal State:
*/
CREATE TABLE token_bucket (
 last_update TIMESTAMP
 tokens INTEGER 
 time_unit INTEGER
)

/*
Initilization:
    Insert the parameters
*/
INSERT INTO token_bucket (last_update, tokens) VALUES (CURRENT_TIMESTAMP, @bucket_size, @time_unit);


/*
  Processing Logic:
*/
SET elapsed_time, curr_tokens, time_unit = SELECT TIMESTAMPDIFF(SECOND, last_update, CURRENT_TIMESTAMP), tokens FROM token_bucket
SET new_curr_tokens = curr_tokens + time_diff * curr_tokens / time_unit
SET rpc_forward_count = LEAST(SELECT COUNT(*) FROM input, new_curr_tokens)

UPDATE token_bucket SET curr_tokens=(new_curr_tokens-rpc_forward_count), last_update=CURRENT_TIMESTAMP

CREATE TABLE output AS SELECT * FROM input LIMIT rpc_forward_count;
