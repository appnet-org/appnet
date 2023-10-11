import re

from ir.frontend.parser import IRParser
from ir.frontend.transformer import IRTransformer


class IRCompiler:
    def __init__(self):
        self.parser = IRParser()
        self.transformer = IRTransformer()

    def compile(self, spec: str):
        # parsing
        ast = self.parser.parse(spec)
        # print(ast.pretty())
        ir = self.transformer.transform(ast)
        ir.display()
