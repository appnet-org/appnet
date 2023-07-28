import re

from graph_compiler.frontend.parser import GraphParser
from graph_compiler.frontend.transformer import GraphTransformer


class GraphCompiler:
    def __init__(self):
        self.parser = GraphParser()
        self.transformer = GraphTransformer()

    def compile(self, spec: str):
        # parsing
        ast = self.parser.parse(spec)
        # print(ast.pretty())
        graph = self.transformer.transform(ast)
        graph.display()
