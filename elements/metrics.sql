-- Logging
SET req_num = 0;

--processing--
SET req_num = req_num + SELECT COUNT(*) FROM input;

INSERT INTO output 
SELECT * FROM input;
