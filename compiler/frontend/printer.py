from tree.node import Node

from compiler.tree.visitor import *


class Printer(Visitor):
    """
    ctx: indent (width=4)
    """

    def visitRoot(self, node: List[Statement], ctx: int = 0) -> None:
        for statement in node:
            print(statement.accept(self, ctx))

    def visitValue(self, node: Value, ctx: int) -> str:
        return add_indent([f"{node.name}({str(node.value)})"], ctx)

    def visitVariableValue(self, node: VariableValue, ctx: int) -> str:
        return add_indent([f"Variable::{node.value}"], ctx)

    def visitColumnValue(self, node: ColumnValue, ctx: int) -> str:
        # print("visitColumnValue", node.table_name, node.column_name)
        content = (
            node.column_name
            if node.table_name == ""
            else f"{node.table_name}.{node.column_name}"
        )
        return add_indent([f"Column::{content}"], ctx)

    def visitFunctionValue(self, node: FunctionValue, ctx: int) -> str:
        ret = []
        for para in node.parameters:
            ret.append(para.accept(self, ctx))
        ret = ",".join(ret)
        return add_indent([f"Function::{node.value}({ret})"], ctx)

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
            "   " + node.select_stmt.accept(self, 2),
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
            f"columns:{', '.join(c.accept(self, 0) for c in node.columns)}",
            f"from:{node.from_table}",
        ]
        if node.aggregator is not None:
            res.append(f"aggregator: {node.aggregator.accept(self, 0)}")
        if node.join_clause is not None:
            res.append(node.join_clause.accept(self, 1))
        if node.where_clause is not None:
            res.append(node.where_clause.accept(self, 1))
        if node.limit is not None:
            res.append(node.limit.accept(self, 1))

        return "; ".join(res)

    def visitSetStatement(self, node: SetStatement, ctx: int) -> str:
        res = [
            "SetStatement",
            f"    {node.variable.accept(self, 0)} = {node.expr.accept(self, 0)}",
        ]
        return add_indent(res, ctx)

    def visitJoinClause(self, node: JoinClause, ctx: int) -> str:
        res = [
            f"JoinClause table: {node.table_name}\n{node.condition.accept(self, ctx + 3)}"
        ]
        return add_indent(res, ctx)

    def visitCompareOp(self, node: CompareOp, ctx: int) -> str:
        if node == CompareOp.EQ:
            res = "=="
        elif node == CompareOp.NEQ:
            res = "!="
        elif node == CompareOp.GT:
            res = ">"
        elif node == CompareOp.LT:
            res = "<"
        elif node == CompareOp.GE:
            res = ">="
        elif node == CompareOp.LE:
            res = "<="
        else:
            raise ValueError("Unrecognized operator")
        return add_indent([res], ctx)

    def visitLogicalOp(self, node: LogicalOp, ctx: int) -> str:
        if node == LogicalOp.AND:
            res = "AND"
        elif node == LogicalOp.OR:
            res = "OR"
        else:
            raise ValueError("Unrecognized operator")
        return add_indent([res], ctx)

    def visitArithmeticOp(self, node: ArithmeticOp, ctx: int) -> str:
        if node == ArithmeticOp.ADD:
            res = "+"
        elif node == ArithmeticOp.SUB:
            res = "-"
        elif node == ArithmeticOp.MUL:
            res = "*"
        elif node == ArithmeticOp.DIV:
            res = "/"
        else:
            raise ValueError("Unrecognized operator")
        return add_indent([res], ctx)

    def visitAggregator(self, node: Aggregator, ctx: int) -> str:
        if node == Aggregator.COUNT:
            res = "COUNT"
        elif node == Aggregator.SUM:
            res = "SUM"
        elif node == Aggregator.AVG:
            res = "AVG"
        elif node == Aggregator.MAX:
            res = "MAX"
        elif node == Aggregator.MIN:
            res = "MIN"
        else:
            raise ValueError("Unrecognized operator")
        return add_indent([res], ctx)

    def visitSearchCondition(self, node: SearchCondition, ctx: int) -> str:
        lvalue_str = node.lvalue.accept(self, 0)
        rvalue_str = node.rvalue.accept(self, 0)
        # print("lvalue_str", lvalue_str, "rvalue_str", rvalue_str)
        if isinstance(node.operator, LogicalOp):
            lvalue_str = "(" + lvalue_str + ")"
            rvalue_str = "(" + rvalue_str + ")"
        res = [f"{lvalue_str} {node.operator.accept(self, 0)} {rvalue_str}"]
        return add_indent(res, ctx)

    def visitWhereClause(self, node: WhereClause, ctx: int) -> str:
        res = [f"WhereClause {node.search_condition.accept(self, 0)}"]
        return add_indent(res, ctx)

    def visitExpression(self, node: Expression, ctx: int) -> str:
        res = f"{node.lvalue.accept(self, 0)} {node.operator.accept(self, 0)} {node.rvalue.accept(self, 0)}"
        return res
