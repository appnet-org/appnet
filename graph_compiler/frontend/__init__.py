import re

from graph_compiler.frontend.parser import GraphParser


class GraphCompiler:
    def __init__(self):
        self.parser = GraphParser()

    def compile(self, spec: str):
        # parsing
        ast = self.parser.parse(spec)
        print(ast)
