import re

from ir.frontend.parser import IRParser
from ir.frontend.transformer import IRTransformer
from ir.frontend.printer import Printer
from ir.node import Program

class IRCompiler:
    def __init__(self):
        self.parser = IRParser()
        self.transformer = IRTransformer()

    def compile(self, spec: str) -> Program:
        # parsing
        ast = self.parser.parse(spec)
        # print(ast.pretty())
        ir = self.transformer.transform(ast)
        return ir