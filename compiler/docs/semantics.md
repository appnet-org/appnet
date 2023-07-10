# Ovewview

ADN uses a SQL-like language to describe the network functions. Currently, we only discuss the logic within a single network function. Further more, we only consider NF that operates on a single RPC message without batching.

# Core Concepts

ADN NF uses several core concepts: `input`, `output`. Those concepts are assumed as prior knowledge and does not appear in the SQL code.

## `input` table

This represent the inbound RPC messages, or ingress traffic. We assume that there is a single RPC message in the `input` table. During the execution of the NF, we can access the `input` table by `SELECT` statement many times.
Althrough the backend may differ in the implementation, we assume an RPC is a struct that has metadata and data. Our compiler will do a mapping to map the abstract fields to lowlevel fields. Note that `rpc_meta` contains the information that is irrelevant to the protofile, such as `src` and `dst`, and `data` is an opaque fields that type is defined by protofile.

```c
struct rpc_meta {
    char *type,
    char *src,
    char *dst,
    // possibly more fields
}
struct rpc {
  rpc_meta *metadata;
  void *data,
}
```

For simplicity, we can access the proto fields by `input.data.field_name` and metadata like `input.metadata.src` in SQL code.

Note that you can only `consume` or `read` from `input` table, i.e. you can only `SELECT` from `input` table. You cannot `INSERT` into `input` table.

## `output` table

This represent the outbound RPC messages, or egress traffic. We need to `INSERT` into `output` table to send a RPC message, and that RPC must match the type of `input`. Maybe we should allow multiple type in `output` table, but currently we only support one type.

If we want to drop a RPC message, we simply do not `INSERT` into `output` table or do not `CREATE` the `output` table.

Note that you can only `produce` or `write` to `output` table, i.e. you can only `INSERT` into `output` table. You cannot `SELECT` from `output` table.
