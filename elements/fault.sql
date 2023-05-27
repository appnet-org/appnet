/*
Initilization:
*/
SET @probability = probability

/*
  Processing Logic: Drop requests based on the preset probability
*/
CREATE TABLE output AS 
SELECT * from input WHERE random() < @probability;