import argparse
import os

from graph_compiler.frontend import GraphCompiler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", "-s", required=True, type=str)
    args = parser.parse_args()

    assert os.path.isfile(args.spec), "spec file does not exist"
    spec = open(args.spec, "r").read()

    compiler = GraphCompiler()
    compiler.compile(spec)