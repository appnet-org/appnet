-- Rate Limiting
CREATE TABLE token_bucket (
 last_update TIMESTAMP
 tokens INTEGER 
)

-- initialize the token bucket with 10 tokens
INSERT INTO token_bucket (last_update, tokens) VALUES (CURRENT_TIMESTAMP, @bucket_size);

CREATE PROCEDURE rate_limiting @bucket_size INT, @request_per_second INT
AS 
SELECT TIMESTAMPDIFF(SECOND, last_update, CURRENT_TIMESTAMP)
-- INTO elapsed_time
FROM token_bucket

-- caculate the current number of tokens
SET curr_tokens = LEAST(tokens + elapsed_time * @request_per_second, @bucket_size);
SET num_rpc = (SELECT COUNT(*) FROM input);

-- Check if there are enough tokens avaliable
IF curr_tokens >= num_rpc 
  -- Update the token bucket
  UPDATE token_bucket
  SET tokens = curr_tokens - num_rpc, last_update = CURRENT_TIMESTAMP
  --  Create the output table
  CREATE TABLE output AS
  SELECT * from INPUT;
ELSE
  SELECT CONCAT('Not enough tokens available. Tokens available: ', curr_tokens) as message




SELECT (julianday(CURRENT_TIMESTAMP) - julianday(last_update)) * 86400.00  FROM token_bucket;