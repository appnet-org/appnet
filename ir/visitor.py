"""
Module that defines the base type of visitor.
"""


from __future__ import annotations

from typing import Callable, List, Protocol, Sequence, TypeVar

from ir.node import *


def accept(visitor: Visitor, ctx) -> Callable:
    return lambda node: node.accept(visitor, ctx)


# collection chainmap
class Visitor(ABC):
    def visitNode(self, node: Node, ctx):
        raise Exception(f"visit function for {node.__class__.__name__} not implemented")

    def visitProgram(self, node: Program, ctx):
        return self.visitNode(node)

    def visitInternal(self, node: Internal, ctx):
        return self.visitNode(node)
    
    def visitProcedure(self, node: Procedure, ctx):
        return self.visitNode(node)
    
    def visitStatement(self, node: Statement, ctx):
        return self.visitNode(node)
    
    def visitMatch(self, node: Match, ctx):
        return self.visitNode(node)
    
    def visitAssign(self, node: Assign, ctx):
        return self.visitNode(node)
    
    def visitPattern(self, node: Pattern, ctx):
        return self.visitNode(node)
    
    def visitExpr(self, node: Expr, ctx):
        return self.visitNode(node)
    
    def visitIdentifier(self, node: Identifier, ctx):
        return self.visitNode(node)
    
    def visitFuncCall(self, node: FuncCall, ctx):
        return self.visitNode(node)
    
    def visitMethodCall(self, node: MethodCall, ctx):
        return self.visitNode(node)
    
    def visitSend(self, node: Send, ctx):
        return self.visitNode(node)
    
    def visitLiteral(self, node: Literal, ctx):
        return self.visitNode(node)
    
    

