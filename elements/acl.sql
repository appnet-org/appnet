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
('RW', 'user1'),
('RO', 'user2');

/*
Processing Logic:
*/
CREATE PROCEDURE acl AS 
CREATE TABLE output AS
SELECT * from input JOIN acl on input.user = acl.name
WHERE acl.permission = "RW";

-- create table input (user varchar(255));
INSERT INTO input (user) VALUES ('Alice');