"""
Module that defines the base type of visitor.
"""


from __future__ import annotations

from typing import Callable, Protocol, Sequence, TypeVar

from compiler.frontend.ast import Statement

from .ast import *


def accept(visitor: Visitor, ctx) -> Callable:
    return lambda node: node.accept(visitor, ctx)


class Visitor:
    def visitOther(self, node: Node, ctx) -> None:
        return None

    def visitStatement(self, node: Statement, ctx):
        return self.visitOther(node, ctx)


class Printer(Visitor):
    def visitStatement(self, node: Statement, ctx):
        print("Statement", node.name, node.type)
