"""
Module that defines the base type of visitor.
"""


from __future__ import annotations

from typing import Callable, List, Protocol, Sequence, TypeVar

from codegen.codegen import init_ctx
from codegen.context import *
from codegen.snippet import *
from frontend.ast import *
from frontend.ast import InsertSelectStatement, SelectStatement
from frontend.visitor import Visitor


class CodeGenerator(Visitor):
    def __init__(self):
        super().__init__()

    def visitRoot(self, node: List[Statement], ctx: Context) -> None:
        for statement in node:
            statement.accept(self, ctx)

    def visitCreateTableStatement(
        self, node: CreateTableStatement, ctx: Context
    ) -> None:
        table_name = node.table_name
        if table_name == "output":
            raise ValueError(
                "Output table should be created by create table as statement"
            )
        struct_name = "struct_" + table_name
        rust_struct = RustStructType(
            struct_name, [trans_col_rust(i) for i in node.columns]
        )
        table = Table(
            table_name, [trans_col(table_name, i) for i in node.columns], rust_struct
        )
        # print(rust_struct)
        if ctx.tables.get(table_name) is None:
            ctx.tables[table_name] = table
        else:
            raise ValueError("Table already exists")

        if table_name.endswith("_file"):
            file_name = "file_" + table_name
            ctx.def_code.append(
                rust_struct.gen_definition()
                + "\n"
                + rust_struct.gen_copy_constructor()
                + "\n"
                + rust_struct.gen_trait_display()
            )
            # ? use append
            ctx.rust_vars.update(
                {
                    table_name: RustVariable(
                        file_name,
                        RustBasicType("File"),
                        True,
                        "create_log_file()",
                        table,
                    )
                }
            )
        else:
            vec_name = "vec_" + table_name
            ctx.def_code.append(
                rust_struct.gen_definition() + "\n" + rust_struct.gen_copy_constructor()
            )
            ctx.rust_vars.update(
                {
                    table_name: RustVariable(
                        vec_name,
                        RustContainerType("Vec", rust_struct),
                        True,
                        None,
                        table,
                    )
                }
            )

    def visitCreateTableAsStatement(self, node: CreateTableAsStatement, ctx: Context):
        new_table_name = node.table_name

        if new_table_name != "output":
            raise NotImplementedError("Currently only output table is supported")

        if new_table_name == "output":
            ctx.is_forward = True

        select = node.select_stmt

        select.accept(self, ctx)
        select_code = ctx.pop_code()

        if new_table_name == "output" and ctx.is_forward == True:
            ctx.is_forward = False

        code = f"let {new_table_name}: Vec<_> = {select_code};"

        ctx.push_code(code)

    def visitInsertSelectStatement(self, node: InsertSelectStatement, ctx):
        table_name = node.table_name

        table = ctx.tables.get(table_name)
        if table is None:
            raise ValueError("Table does not exist")

        var_name = ctx.rust_vars[table_name].name

        columns = ", ".join([i.column_name for i in node.columns])

        select = node.select_stmt
        select.to_table = table_name
        select.accept(self, ctx)
        select_code = ctx.pop_code()

        code = f"for event in {select_code} {{"
        if table_name.endswith("file"):
            code += f'write!(self.{var_name}, "{{}}", event);'
        else:
            code += f"{var_name}.push(event);"
        code += f"}}"

        ctx.push_code(code)

    def visitSelectStatement(self, node: SelectStatement, ctx: Context):
        assert len(node.join_clauses) == 0
        assert len(node.where_clauses) == 0

        table_from = node.from_table
        # print(table_from)
        if ctx.tables.get(table_from) is None:
            raise ValueError("Table does not exist")
        table_from = ctx.tables[table_from]
        table_from_name = table_from.name

        columns = [i.column_name for i in node.columns]
        if columns == ["*"]:
            columns = [i.cname for i in table_from.columns]

        if table_from_name == "input" and ctx.is_forward == True:
            columns = [i for i, _ in table_from.struct.fields]
            columns = [f"req.{i}.clone()" for i in columns]
            columns = ", ".join(columns)
        elif table_from_name == "input":
            # TODO test protobuf
            columns = [input_mapping(i) for i in columns]
            columns = ", ".join(columns)
        else:
            columns = [f"req.{i.cname}.clone()" for i in columns]
            columns = ", ".join(columns).replace(
                "req.CURRENT_TIMESTAMP.clone()", "Utc::now()"
            )

        if node.to_table == "":
            struct = table_from.struct
        else:
            table_to_name = node.to_table
            if ctx.tables.get(table_to_name) is None:
                raise ValueError("Table does not exist")
            table_to = ctx.tables[table_to_name]
            struct = table_to.struct

        if ctx.is_forward == True:
            code = f"{table_from_name}.iter().map(|req| RpcMessageGeneral::TxMessage(EngineTxMessage::RpcMessage({struct.name}::new({columns})))).collect::<Vec<_>>()"
        else:
            code = f"{table_from_name}.iter().map(|req| {struct.name}::new({columns})).collect::<Vec<_>>()"

        ctx.push_code(code)
