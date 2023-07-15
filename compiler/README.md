# Get Started

We translate each SQL statement to corresponding Rust code.

First we need to clone  mrpc repo.

```bash
# in ~
git clone https://github.com/livingshade/phoenix.git
cd phoenix
git switch adn
# Change the path of phoenix(mrpc) in `compiler/codegen/template.py` before running.
```

```bash
# in compiler
bash ./install.sh
python3 main.py -p [ENGINE_NAME]
#! Currently, ENGINE_NAME must be `logging`
# Change working directory to `phoenix`, you will found generated `nofile-logging` engine.
```

Then, refer to tutorial in `phoenix/mdbooks` to add the `nofile-logging` engine.

# Overveiw

```
compiler
|---- backend       # backend code (currently only mRPC rust)
|---- codegen       # generate backend code from SQL
|---- docs          # documents, rules, etc.
|---- frontend      # frontend code (SQL)
  |---- parser      # parse lark-generated AST to our AST
|---- protobuf      # protobuf related code
|---- tree          # AST definition, visitor. Unfortunatly "ast" is used in Python, so we use "tree" instead.
install.sh          # you should run this script before running main.py
main.py             # main entry
```


### todos

- We use clone(copy) rather than move(reference) in constructors, which is not good.
- We should use `&str` rather than `String` for string literals.
- We should move result from `input` into `output` rather than copy it.

## Logging

Currently, we only support logging element.

We can generated Rust code that store each inbound RPC message into a vector(table).

- We does not write to a file or to stdout, so it is "invisible". Maybe we need to change SQL sematic, i.e. add keyword like `print`.

- We does not parse the rpc data, so currently only metadata is stored. Since RPC format depends on its protobuf config, and we have not yet import that config into our code.

### SQL Code
