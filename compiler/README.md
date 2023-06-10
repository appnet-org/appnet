# Compiler Design

We translate each SQL statement to corresponding Rust code.

```bash
python3 main.py -p [ENGINE_NAME]
# you will find the generated Rust code in ./generated
# split, and copy the code to ./compiler_test/src/main{number}.rs
# This is already done in this repo.
cd compiler_test
cargo run --bin logging # acl, fault
# see the result
```

### todos

- We use clone(copy) rather than move(reference) in constructors, which is not good.
- We should use `&str` rather than `String` for string literals.
- We should move result from `input` into `output` rather than copy it.

## Logging



### SQL Code 

