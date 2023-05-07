-- Random Load Balancer

/*
Processing Logic: 
*/
CREATE TABLE output AS
SELECT *, new_random_dst() as dst_svc_replica  FROM INPUT;
