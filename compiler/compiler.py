from lark import Lark
import sys
from parser.parser import *
from codegen.codegen import *
from codegen.template import generate


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
        return self.Transformer.transform(ast)

    def compile(self, sql, ctx):
        ast = self.transform(sql)
        if self.verbose:
            print(ast)
        return compile_sql_to_rust(ast, ctx)

    def generate(self, e):
        return generate(e)