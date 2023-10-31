/*
  Internal State
*/
CREATE TABLE ab_testing_header (
  service_name VARCHAR(255)
  header_value VARCHAR(255)
);

/*
Initilization:
    Insert the parameters
*/
INSERT INTO ab_testing_header (service_name, header_value)
VALUES
("service_a", "Jason"),
("service_b", "Peter"),
("service_c", "Bob");



/*
  Processing Logic:
  NOTE: Needs to verify the correctness of this query
*/
CREATE TABLE output_table AS
SELECT input_table.*, ab_testing_header.service_name
FROM input_table
JOIN ab_testing_header
ON input_table.header_value = ab_testing_header.header_value;
