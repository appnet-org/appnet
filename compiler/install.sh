# install python dependencies
pip install lark pre-commit tomli tomli_w

COMPILER_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(dirname $COMPILER_DIR)
export PYTHONPATH=$PYTHONPATH:$COMPILER_DIR:$ROOT_DIR
export PHOENIX_DIR="$HOME/phoenix"
