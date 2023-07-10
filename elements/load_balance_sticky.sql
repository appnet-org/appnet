-- Sticky Load Balancer based on a RPC field

/*
Internal state:
    lb: stores the mapping from flow_id to dst_svc
*/
CREATE TABLE lb_tab (
    flow_id INT,
    dst_svc_replica VARCHAR(255)
);

/*
Processing Logic:
1. Create a lb_update view that select dst_svc for new RPC
2. Update the lb table with the new dst_svc
3. Set the dst_svc for all RPCs
*/

CREATE VIEW lb_update AS
SELECT flow_id, new_random_dst() as dst_svc_replica
FROM input LEFT JOIN lab_tab on flow_id
WHERE lb_tab.flow_id IS NULL;

INSERT INTO lb SELECT * FROM lb_update;

CREATE TABLE output AS
SELECT *, lb.dst_svc_replica FROM input
JOIN lb_tab on input.flow_id = lb_tab.flow_id;
