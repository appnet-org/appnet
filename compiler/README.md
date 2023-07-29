# Get Started

We translate each SQL statement to corresponding Rust code.

First we need to clone  mrpc repo.

```bash
# in ~
git clone https://github.com/livingshade/phoenix.git
cd phoenix
git switch adn
```

```bash
# in compiler
. ./install.sh
python3 main.py -e [ENGINE_NAME_CHAIN] --mrpc_dir [MRPC_PATH]
# For example:
# python main.py -e "logging->logging" --mrpc_dir ../../phoenix/experimental/mrpc
```

- ENGINE_NAME_CHAIN
  - should be a chain of engine names, separated by `->`. For example, `logging->logging` means that we have two logging engine. `fault->logging` means that we have a fault engine followed by a logging engine. Currently we only support `logging` and `fault`.

- MRPC_PATH
  - which is the path to mRPC repo. It should be something like `${PATH_TO_PHOENIX}/phoenix/experimental/mrpc`.
  - By default it is `/users/${UserName}/phoenix/experimental/mrpc`.

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
