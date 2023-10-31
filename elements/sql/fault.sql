/*
Initialization:
*/
SET probability = 0.9;

--processing--

/*
  Processing Logic: Drop requests based on the preset probability
*/
INSERT INTO output 
SELECT * FROM input WHERE random() < probability;
