import sys

from codegen.codegen import *
from codegen.template import generate
from frontend.parser import *
from codegen.context import *
from lark import Lark


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

    def compile(self, sql, ctx: Context):
        return visit_root(sql, ctx)

    def generate(self, engine: str, ctx: Context):
        return generate(engine, ctx)
