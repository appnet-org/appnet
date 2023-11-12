-- Access Control List

/*
Internal state:
    acl: A table to store access control rules
*/
CREATE TABLE acl (
  name VARCHAR(255),
  permission VARCHAR(2)
);

/*
Initilization:
    Insert the access control rules into the acl table
*/
INSERT INTO acl (name, permission) VALUES ('danyang', 'N');

--processing--

/*
Processing Logic: block users that do not have permission
*/
INSERT INTO output
SELECT * FROM input JOIN acl ON input.customer_name = acl.name
WHERE acl.permission != 'N';
