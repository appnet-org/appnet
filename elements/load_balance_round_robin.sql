/*
Processing Logic: 
TODO: number of repliaca is needs to be defined. 
*/
CREATE TABLE output AS
SELECT *, (ROW_NUMBER() OVER () - 1) % @number_of_replica AS new_column
FROM input;