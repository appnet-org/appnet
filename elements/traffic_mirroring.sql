-- Traffic Mirroring

/*
Initilization:
 NOTE: this can be store as a table so that there can be multiple mirroring rules
*/
SET mirror = "service_address"

/*
  Processing Logic:
*/

INSERT INTO output SELECT * FROM input;
UPDATE output SET meta_dst = mirror;

INSERT INTO output SELECT * FROM input;

