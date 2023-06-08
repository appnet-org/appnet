from lark import Lark
import sys
from parser.parser import *
from codegen.codegen import *


class ADNCompiler:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.parser = ADNParser()
        self.Transformer = ADNTransformer()

    def parse(self, sql):
        return self.parser.parse(sql)
        
    def transform(self, sql):
        ast = self.parse(sql)
        if self.verbose:
            print(ast)
            # print(ast.pretty())
        return self.Transformer.transform(ast)

    def compile(self, sql):
        ast = self.parse(sql)
        # print(ast.pretty())
        return generate_rust_code(ast)
