/*
Initilization:
*/
SET probability = 0.2;

--processing--

/*
  Processing Logic: Drop requests based on the preset probability
*/
CREATE TABLE output AS
SELECT * FROM input WHERE random() < probability;
