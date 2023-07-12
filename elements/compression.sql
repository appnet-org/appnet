/*
  Processing Logic: Drop requests based on the preset probability
*/
CREATE TABLE output
SELECT compressed(*) from input;
