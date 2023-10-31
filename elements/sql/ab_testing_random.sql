/*
  Internal State
*/
CREATE TABLE ab_testing_random (
  service_name VARCHAR(255)
  probability FLOAT
);

/*
Initilization:
    Insert the parameters
*/
INSERT INTO ab_testing_random (service_name, probability)
VALUES
("service_a", 0.1),
("service_b", 0.2),
("service_c", 0.7);



/*
  Processing Logic:
  NOTE: Needs to verify the correctness of this query
*/
CREATE TABLE output AS
SELECT input.*, ab_testing_random.service_name
FROM input
JOIN (
    SELECT service_name, probability, SUM(probability) OVER () AS total_probability
    FROM ab_testing_random
) AS ab_testing_random
ON RAND() <= ab_testing_random.probability / ab_testing_random.total_probability
ORDER BY RAND();
