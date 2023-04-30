/* 
Internal state: 
    acl: A table to store access control rules
*/
CREATE TABLE acl (
  name VARCHAR(255),
  permission CHAR(2) not null
);

/*
Initilization:
    Insert the access control rules into the acl table
*/
INSERT INTO acl (permission, name) VALUES
('Y', 'Alice'),
('N', 'Bob'),
('Y', 'Peter'),
('Y', 'Jeff'),
('Y', 'Bill');

/*
Processing Logic: block users that do not have permission
*/
CREATE TABLE output AS
SELECT * from input JOIN acl on input.name = acl.name
WHERE acl.permission = "Y";
