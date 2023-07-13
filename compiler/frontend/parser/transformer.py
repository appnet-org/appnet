from frontend.ast import *
from lark import Transformer


class ADNTransformer(Transformer):
    def __init__(self):
        self.variables = {}

    def start(self, n):
        # print("start", n)
        return n

    def statement(self, s):
        s = s[0]
        return s

    def create_table_as_statement(self, c):
        return CreateTableAsStatement(c[0]["table_name"], c[1])

    def select_statement(self, s):
        join_clauses, where_clauses = [], []
        for clause in s[2:]:
            if clause.name == "WhereClause":
                where_clauses.append(clause)
            elif clause.name == "JoinClause":
                join_clauses.append(clause)
            else:
                raise ValueError("Unrecognized clause")
        return SelectStatement(
            s[0], s[1]["table_name"], "", join_clauses, where_clauses
        )

    def set_statement(self, n):
        (n,) = n
        self.variables[n["variable"]] = n["value"]
        return SetStatement(n["variable"], n["value"])

    def create_table_statement(self, c):
        columns = []
        for column_dict in c[1:]:
            columns.append((column_dict["column"], column_dict["data_type"]))
        return CreateTableStatement(c[0]["table_name"], columns)

    def insert_value_statement(self, i):
        return InsertValueStatement(i[0]["table_name"], i[1], i[2:])

    def insert_select_statement(self, i):
        i[2].to_table = i[0]["table_name"]
        return InsertSelectStatement(i[0]["table_name"], i[1], i[2])

    def identifier(self, i):
        (i,) = i
        res = {"variable": i.value}
        return res

    def number(self, n):
        # print(n)
        (n,) = n
        return NumberValue(n.value)
        # res = {"data_type": "number", "value": n.value}
        # return res

    def assignment(self, a):
        res = {
            "type": "assignment",
            "variable": a[0]["variable"],
            "value": a[1]
            # "value": a[1]["value"],
            # "data_type": a[1]["data_type"],
        }
        # print("assignment", n)
        return res

    def data_type(self, d):
        (d,) = d
        # print("data_type", d)
        res = {"data_type": d.value}
        return res

    def length(self, l):
        (l,) = l
        res = {"length": l.value}
        return res

    def cname(self, c):
        (c,) = c
        if c.value in self.variables:
            return VariableValue(c.value)
        else:
            return ColumnValue("", c.value)

    def column_definition(self, c):
        # print("column_definition", c)
        column = ColumnValue("", c[0].column_name)
        length = c[2]["length"] if c[2] != None and "length" in c[2] else 0
        type_name = c[1]["data_type"]
        if type_name == "TIMESTAMP":
            data_type = TimestampType(length)
        elif type_name == "VARCHAR":
            data_type = VarCharType(length)
        elif type_name == "FILE":
            data_type = FileType(length)
        else:
            raise ValueError(f"Unsupported type '{type_name}'")
        res = {"column": column, "data_type": data_type}
        return res

    def table_name(self, t):
        (t,) = t
        res = {"table_name": t.value}
        return res

    def quoted_string(self, s):
        (s,) = s
        return StringValue(s.value)

    def string(self, s):
        return s[0]

    def value_list(self, v):
        return v

    def column_list(self, c):
        return c
        # columns = [column["name"] for column in c]
        # print("column_list", columns)
        # res = {"columns": columns}
        # return res

    def all(self, a):
        # print("all", a)
        return ColumnValue("", "*")

    def select_list(self, s):
        return s

    def l(self, l):
        return "<"

    def random_func(self, r):
        return "random"

    def function(self, f):
        return FunctionValue(f[0])

    def comparison_condition(self, c):
        return SearchCondition(c[0], c[2], c[1])

    def eq(self, c):
        return "=="

    def neq(self, c):
        return "!="

    def g(self, c):
        return ">"

    def l(self, c):
        return "<"

    def ge(self, c):
        return ">="

    def le(self, c):
        return "<="

    def search_and_condition(self, c):
        return SearchCondition(c[0], c[1], "AND")

    def search_or_condition(self, c):
        return SearchCondition(c[0], c[1], "OR")

    def search_condition(self, s):
        (s,) = s
        return s

    def where_clause(self, w):
        # print("where_clause", w)
        (w,) = w
        return WhereClause(w)

    def join_clause(self, j):
        return JoinClause(j[0]["table_name"], j[1], j[2])
        # ColumnValue(j[1]["table_name"], j[1]["column_name"]),
        # ColumnValue(j[2]["table_name"], j[2]["column_name"]),

    def column_field(self, c):
        return ColumnValue(c[0]["table_name"], c[1]["variable"])
