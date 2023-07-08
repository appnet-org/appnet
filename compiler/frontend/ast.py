from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Union


class Node(ABC):
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__

    def accept(self, visitor, ctx):
        func_name = "visit" + self.name
        visit_func = getattr(visitor, func_name)
        return visit_func(visitor, self, ctx)


class Value(Node):
    @property
    def type(self) -> str:
        return "Value"


class ColumnValue(Value):
    def __init__(self, table_name: str, column_name: str):
        self.table_name = table_name
        self.column_name = column_name


class NumberValue(Value):
    def __init__(self, value: Union[str, int, float]):
        self.value = float(value)


class FunctionValue(Value):
    def __init__(self, func_name: str):
        self.func_name = func_name


class VariableValue(Value):
    def __init__(self, var_name: str):
        self.var_name = var_name


class StringValue(Value):
    def __init__(self, value: str):
        self.value = value


class Statement(Node):
    def __init__(self):
        pass

    @property
    def type(self) -> str:
        return "Statement"


class CreateTableStatement(Statement):
    def __init__(self, table_name: str, columns: List[Dict[str, str]]):
        super().__init__()
        self.table_name = table_name
        self.columns = dict()
        for column in columns:
            data_length = int(column["length"]) if "length" in column else 0
            self.columns[column["column_name"]] = {
                "data_type": column["data_type"],
                "data_length": data_length,
            }


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
        self.columns = self.columns
        self.select_stmt = select_stmt


class SearchCondition(Node):
    def __init__(self, lvalue: SearchCondition, rvalue: SearchCondition, operator: str):
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
    def __init__(self, table_name: str, lvalue: Value, rvalue: Value):
        super().__init__()
        self.table_name = table_name
        self.lvalue = lvalue
        self.rvalue = rvalue


class SelectStatement(Statement):
    def __init__(
        self,
        columns: List[ColumnValue],
        table_name: str,
        join_clauses: List[JoinClause],
        where_clauses: List[WhereClause],
    ):
        super().__init__()
        self.columns = columns
        self.from_table = table_name
        self.join_clauses = join_clauses
        self.where_clauses = where_clauses


class SetStatement(Statement):
    def __init__(self, variable: VariableValue, value: Value):
        super().__init__()
        self.variable = variable
        self.value = value
