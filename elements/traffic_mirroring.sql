-- Traffic Mirroring

/*
Initilization:
 NOTE: this can be store as a table so that there can be multiple mirroring rules
*/
SET @service_name = service_name

/*
  Processing Logic:
*/
CREATE TABLE output AS
SELECT *
FROM input
UNION ALL
SELECT *, @service_name AS dst_svc
FROM input;
