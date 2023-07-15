import sys

from lark import Lark

from compiler.codegen.context import Context
from compiler.codegen.finalizer import finalize
from compiler.codegen.generator import CodeGenerator
from compiler.frontend.parser import ADNParser, ADNTransformer


class ADNCompiler:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.parser = ADNParser()
        self.Transformer = ADNTransformer()
        self.generator = CodeGenerator()

    def parse(self, sql):
        return self.parser.parse(sql)

    def transform(self, sql):
        ast = self.parse(sql)
        if self.verbose:
            print(ast)
        return self.Transformer.transform(ast)

    def compile(self, sql, ctx: Context):
        return self.generator.visitRoot(sql, ctx)
        # return visit_root(sql, ctx)

    def generate(self, engine: str, ctx: Context, output_dir: str):
        return finalize(engine, ctx, output_dir)
