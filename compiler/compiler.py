from lark import Lark
import sys
from parser.parser import *
from codegen.codegen import *


class ADNCompiler:
    def __init__(self):
        self.parser = ADNParser()

    def parse(self, sql):
        return self.parser.parse(sql)

    def compile(self, sql):
        ast = self.parse(sql)
        # print(ast.pretty())
        return generate_rust_code(ast)
