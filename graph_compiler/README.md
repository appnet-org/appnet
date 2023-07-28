# Get Started

Run `install.sh` to set environment variables.

```bash
# in graph_compiler/
git switch graph
cd graph_compiler
. ./install.sh
```

Run `main.py` to compile.

```bash
python3 main.py -s [GRAPH_SPECIFICATION_PATH]
```

# Overview

```
graph_compiler
├── example_spec
│   └── logging_acl_delay.spec
├── frontend            # generate GraphIR from spec
│   ├── grammar.lark    # graph specification grammar
│   ├── __init__.py
│   ├── parser.py
│   └── transformer.py
├── graphir             # GraphIR definitions & optimizations
│   └── __init__.py
├── install.sh          # run it to configure the environment
├── main.py             # main entry
└── README.md
```
