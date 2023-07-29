"""
Module that defines the base type of visitor.
"""


from __future__ import annotations

from typing import Callable, List, Protocol, Sequence, TypeVar

from compiler.tree.node import *


def accept(visitor: Visitor, ctx) -> Callable:
    return lambda node: node.accept(visitor, ctx)


# collection chainmap
class Visitor(ABC):
    def visitNode(self, node: Node, ctx):
        raise Exception(f"visit function for {node.name} not implemented")

    def visitRoot(self, node: List[Statement], ctx) -> None:
        pass

    def visitValue(self, node: Value, ctx):
        pass

    def visitColumnValue(self, node: ColumnValue, ctx):
        pass

    def visitDataType(self, node: DataType, ctx):
        pass

    def visitCreateTableStatement(self, node: CreateTableStatement, ctx):
        pass

    def visitCreateTableAsStatement(self, node: CreateTableAsStatement, ctx):
        pass

    def visitInsertValueStatement(self, node: InsertValueStatement, ctx):
        pass

    def visitInsertSelectStatement(self, node: InsertSelectStatement, ctx):
        pass

    def visitSelectStatement(self, node: SelectStatement, ctx):
        pass

    def visitSetStatement(self, node: SetStatement, ctx):
        pass

    def visitJoinClause(self, node: JoinClause, ctx):
        pass

    def visitSearchCondition(self, node: SearchCondition, ctx):
        pass

    def visitWhereClause(self, node: WhereClause, ctx):
        pass

    def visitExpression(self, node: Expression, ctx):
        pass


def add_indent(slist: List[str], indent: int) -> str:
    return "\n".join(map(lambda s: " " * 4 * indent + s, slist))
