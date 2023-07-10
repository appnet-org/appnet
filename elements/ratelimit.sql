-- Rate Limiting with token bucket algorithm

/*
  Internal State:
*/
CREATE TABLE token_bucket (
 last_update TIMESTAMP
 tokens INTEGER
 token_per_fill INTEGER
)

/*
Initilization:
    Insert the parameters
*/
INSERT INTO token_bucket (last_update, tokens, token_per_fill) VALUES (CURRENT_TIMESTAMP, 0, @token_per_fill);


/*
  Processing Logic:
    1. Caculate the current tokens and the number of RPCs in input
    2. Caculate how many RPCs can be forwarded
    3. Update the tokens and forward the selected RPCs
*/
SET elapsed_time, curr_tokens, time_unit = SELECT TIMESTAMPDIFF(SECOND, last_update, CURRENT_TIMESTAMP), tokens FROM token_bucket
SET new_curr_tokens = curr_tokens + time_diff * token_per_fill
SET rpc_forward_count = LEAST(SELECT COUNT(*) FROM input, new_curr_tokens)

UPDATE token_bucket SET curr_tokens=(new_curr_tokens-rpc_forward_count), last_update=CURRENT_TIMESTAMP

CREATE TABLE output AS SELECT * FROM input LIMIT rpc_forward_count;
