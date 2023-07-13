# install python dependencies
pip install lark pre-commit

COMPILER_DIR=$(pwd)
ROOT_DIR=$(dirname $(pwd))
echo "export PYTHONPATH=$PYTHONPATH:$COMPILER_DIR:$ROOT_DIR" >> ~/.bashrc
source ~/.bashrc
