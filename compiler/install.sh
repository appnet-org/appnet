# install python dependencies
pip install lark pre-commit tomli tomli_w

COMPILER_DIR=$(pwd)
ROOT_DIR=$(dirname $(pwd))
export PYTHONPATH=$PYTHONPATH:$COMPILER_DIR:$ROOT_DIR
export PHOENIX_DIR="$HOME/phoenix"
