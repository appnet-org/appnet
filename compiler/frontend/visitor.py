"""
Module that defines the base type of visitor.
"""


from __future__ import annotations

from typing import Callable, List, Protocol, Sequence, TypeVar

from frontend.ast import *


def accept(visitor: Visitor, ctx) -> Callable:
    return lambda node: node.accept(visitor, ctx)


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

    def visitCreateTableAsStatement(
        self, node: CreateTableAsStatement, ctx
    ):
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

def add_indent(slist: List[str], indent: int) -> str:
    return "\n".join(map(lambda s: " " * 4 * indent + s, slist))


class Printer(Visitor):
    """
    ctx: indent (width=4)
    """
    def visitRoot(self, node: List[Statement], ctx: int) -> None:
        for statement in node:
            statement.accept(self, ctx)
            
    def visitValue(self, node: Value, ctx: int) -> str:
        return add_indent([f"{node.name}({str(node.value)})"], ctx)

    def visitColumnValue(self, node: ColumnValue, ctx: int) -> str:
        content = (
            node.column_name
            if node.table_name == ""
            else f"{node.table_name}.{node.column_name}"
        )
        return add_indent([f"ColumnValue({content})"], ctx)

    def visitDataType(self, node: DataType, ctx: int) -> str:
        return add_indent([f"{node.name}({node.length})"], ctx)

    def visitCreateTableStatement(self, node: CreateTableStatement, ctx: int) -> str:
        res = [
            "CreateTableStatement",
            f"    table_name: {node.table_name}",
            "    columns:",
        ]
        for column_value, data_type in node.columns:
            res.append(
                f"        {column_value.accept(self, 0)}: {data_type.accept(self, 0)})"
            )
        return add_indent(res, ctx)

    def visitCreateTableAsStatement(
        self, node: CreateTableAsStatement, ctx: int
    ) -> str:
        res = [
            "CreateTableAsStatement",
            f"    table_name: {node.table_name}",
            "    select_stmt:",
            node.select_stmt.accept(self, 2),
        ]
        return add_indent(res, ctx)

    def visitInsertValueStatement(self, node: InsertValueStatement, ctx: int) -> str:
        res = [
            "InsertValueStatement",
            f"    table_name: {node.table_name}",
            f"    columns: {', '.join(c.accept(self, 0) for c in node.columns)}",
            f"    values:",
        ]
        for value_list in node.values:
            value_list_str = (
                "        (" + ", ".join(v.accept(self, 0) for v in value_list) + ")"
            )
            res.append(value_list_str)
        return add_indent(res, ctx)

    def visitInsertSelectStatement(self, node: InsertSelectStatement, ctx: int) -> str:
        res = [
            "InsertSelectStatement",
            f"    table_name: {node.table_name}",
            f"    columns: {', '.join(c.accept(self, 0) for c in node.columns)}",
            "    select_stmt:",
            node.select_stmt.accept(self, 2),
        ]
        return add_indent(res, ctx)

    def visitSelectStatement(self, node: SelectStatement, ctx: int) -> str:
        res = [
            "SelectStatement",
            f"    columns: {', '.join(c.accept(self, 0) for c in node.columns)}",
            f"    from: {node.from_table}",
        ]
        for c in node.join_clauses:
            res.append(c.accept(self, 1))
        for c in node.where_clauses:
            res.append(c.accept(self, 1))
        return add_indent(res, ctx)

    def visitSetStatement(self, node: SetStatement, ctx: int) -> str:
        res = ["SetStatement", f"    {node.variable} = {node.value.accept(self, 0)}"]
        return add_indent(res, ctx)

    def visitJoinClause(self, node: JoinClause, ctx: int) -> str:
        res = [
            f"JoinClause {node.table_name} ON {node.lvalue.accept(self, 0)} = {node.rvalue.accept(self, 0)}"
        ]
        return add_indent(res, ctx)

    def visitSearchCondition(self, node: SearchCondition, ctx: int) -> str:
        lvalue_str = node.lvalue.accept(self, 0)
        rvalue_str = node.rvalue.accept(self, 0)
        if node.operator.isupper():
            lvalue_str = "(" + lvalue_str + ")"
            rvalue_str = "(" + rvalue_str + ")"
        res = [f"{lvalue_str} {node.operator} {rvalue_str}"]
        return add_indent(res, ctx)

    def visitWhereClause(self, node: WhereClause, ctx: int) -> str:
        res = [f"WhereClause {node.search_condition.accept(self, 0)}"]
        return add_indent(res, ctx)
