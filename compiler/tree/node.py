from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import List, Tuple, Union


class Node:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__

    def accept(self, visitor, ctx):
        class_list = type(self).__mro__
        for cls in class_list:
            func_name = "visit" + cls.__name__
            visit_func = getattr(visitor, func_name, None)
            if visit_func is not None:
                return visit_func(self, ctx)
        raise Exception(f"visit function for {self.name} not implemented")


class Value(Node):
    def __init__(self):
        self.data_type = None

    @property
    def type(self) -> str:
        return "Value"


class ColumnValue(Value):
    def __init__(self, table_name: str, column_name: str):
        super().__init__()
        self.table_name = table_name
        self.column_name = column_name


class NumberValue(Value):
    def __init__(self, value: Union[str, int, float]):
        super().__init__()
        self.value = float(value)
        self.data_type = "float"


class FunctionValue(Value):
    def __init__(self, func_name: str):
        super().__init__()
        self.value = func_name


class VariableValue(Value):
    def __init__(self, var_name: str):
        super().__init__()
        self.value = var_name


class StringValue(Value):
    def __init__(self, value: str):
        super().__init__()
        self.value = value
        self.data_type = "string"


class DataType(Node):
    def __init__(self, length: int):
        super().__init__()
        self.length = length

    @property
    def type(self) -> str:
        return "DataType"


class VarCharType(DataType):
    def sql_type(self):
        return "VARCHAR"


class FileType(DataType):
    def sql_type(self):
        return "FILE"


class TimestampType(DataType):
    def sql_type(self):
        return "TIMESTAMP"


class Statement(Node):
    def __init__(self):
        pass

    @property
    def type(self) -> str:
        return "Statement"


class CreateTableStatement(Statement):
    def __init__(
        self, table_name: str, columns: List[Tuple[Union[ColumnValue, DataType]]]
    ):
        super().__init__()
        self.table_name = table_name
        self.columns = columns

    # def accept(self, visitor, ctx):
    # return visitor.visitCreateTableStatement(self, ctx)


class CreateTableAsStatement(Statement):
    def __init__(self, table_name: str, select_stmt: SelectStatement) -> None:
        super().__init__()
        self.table_name = table_name
        self.select_stmt = select_stmt


class InsertValueStatement(Statement):
    def __init__(
        self, table_name: str, columns: List[ColumnValue], values: List[List[Value]]
    ):
        super().__init__()
        self.table_name = table_name
        self.columns = columns
        self.values = values


class InsertSelectStatement(Statement):
    def __init__(
        self, table_name: str, columns: List[ColumnValue], select_stmt: SelectStatement
    ):
        super().__init__()
        self.table_name = table_name
        self.columns = columns
        self.select_stmt = select_stmt


class Operator(Enum):
    def __eq__(self, other: Operator):
        return self.value == other.value

    def accept(self, visitor, ctx):
        class_list = type(self).__mro__
        for cls in class_list:
            func_name = "visit" + cls.__name__
            visit_func = getattr(visitor, func_name, None)
            if visit_func is not None:
                return visit_func(self, ctx)
        raise Exception(f"visit function for {self.name} not implemented")


class CompareOp(Operator):
    EQ = 1
    GT = 2
    LT = 3
    GE = 4
    LE = 5
    NEQ = 6


class LogicalOp(Operator):
    AND = 1
    OR = 2


class SearchCondition(Node):
    def __init__(
        self, lvalue: SearchCondition or Value, rvalue: SearchCondition or Value, operator: Operator
    ):
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.operator = operator

    @property
    def type(self) -> str:
        return "Condition"


class Clause(Node):
    @property
    def type(self) -> str:
        return "Clause"


class WhereClause(Clause):
    def __init__(self, search_condition: SearchCondition):
        self.search_condition = search_condition


class JoinClause(Clause):
    def __init__(self, table_name: str, condition: SearchCondition):
        super().__init__()
        self.table_name = table_name
        self.condition = condition


class SelectStatement(Statement):
    def __init__(
        self,
        columns: List[ColumnValue],
        from_table: str,
        to_table: str,
        join_clauses: List[JoinClause],
        where_clauses: List[WhereClause],
    ):
        super().__init__()
        self.columns = columns
        self.from_table = from_table
        self.to_table = to_table
        self.join_clauses = join_clauses
        self.where_clauses = where_clauses


class SetStatement(Statement):
    def __init__(self, variable: VariableValue, value: Value):
        super().__init__()
        self.variable = variable
        self.value = value
        self.variable.data_type = self.value.data_type
