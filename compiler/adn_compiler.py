import sys

from lark import Lark

from compiler.codegen.codegen import init_ctx
from compiler.codegen.context import Context
from compiler.codegen.finalizer import finalize
from compiler.codegen.generator import CodeGenerator
from compiler.frontend.parser import ADNParser, ADNTransformer
from compiler.graph.element import Element


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

    def gen(self, sql, ctx: Context):
        return self.generator.visitRoot(sql, ctx)
        # return visit_root(sql, ctx)

    def finalize(self, engine: str, ctx: Context, output_dir: str):
        return finalize(engine, ctx, output_dir)

    def compile(self, elem: Element, output_dir: str):
        init, process = elem.sql
        ctx: Context = init_ctx()

        init, process = self.transform(init), self.transform(process)
        # todo verbose
        init = self.gen(init, ctx)
        while ctx.empty() is False:
            ctx.init_code.append(ctx.pop_code())
        ctx.current = "process"
        process = self.gen(process, ctx)
        while ctx.empty() is False:
            ctx.process_code.append(ctx.pop_code())
        return finalize(elem.name, ctx, output_dir)
