"""
Module that defines the base type of visitor.
"""


from __future__ import annotations

from typing import Callable, List, Protocol, Sequence, TypeVar

from codegen.codegen import init_ctx
from codegen.context import *
from codegen.snippet import *
from tree.node import *
from tree.node import InsertSelectStatement, SelectStatement
from tree.visitor import Visitor


class RustTypeGenerator(Visitor):
    def visitNumberValue(self, node: NumberValue, ctx=None) -> RustType:
        return RustBasicType("f32", node.value)


class CodeGenerator(Visitor):
    def __init__(self):
        super().__init__()
        self.type_generator = RustTypeGenerator()

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
        # TODO bubble to ast
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

    def visitInsertSelectStatement(self, node: InsertSelectStatement, ctx: Context):
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

        original_rpc = f"{struct.name}::new({columns})"
        if ctx.is_forward:
            send_logic = f"RpcMessageGeneral::TxMessage(EngineTxMessage::RpcMessage({original_rpc}))"
        else:
            send_logic = original_rpc

        rpc_id = "RpcId::new(unsafe {&*req.meta_buf_ptr.as_meta_ptr()}.conn_id, unsafe {&*req.meta_buf_ptr.as_meta_ptr()}.call_id)"
        error_rpc = f"let error = EngineRxMessage::Ack({rpc_id}, TransportStatus::Error(unsafe {{NonZeroU32::new_unchecked(403)}}),); RpcMessageGeneral::RxMessage(error)"

        for where_clause in node.where_clauses:
            where_clause.search_condition.accept(self, ctx)
            cond_str = ctx.pop_code()
            send_logic = f"if !({cond_str}) {{ {error_rpc} }} else {{ {send_logic} }}"

        code = f"{table_from_name}.iter().map(|req| {send_logic}).collect::<Vec<_>>()"

        ctx.push_code(code)

    def visitSetStatement(self, node: SetStatement, ctx: Context):
        var_name = node.variable.value
        ctx.rust_vars.update(
            {
                var_name: RustVariable(
                    var_name, node.value.accept(self.type_generator, None), False
                )
            }
        )

    def visitFunctionValue(self, node: FunctionValue, ctx: Context):
        if node.value == "random":
            func_str = "rand::random::<f32>()"
        else:
            raise NotImplementedError

        ctx.push_code(func_str)

    def visitVariableValue(self, node: VariableValue, ctx: Context):
        if ctx.rust_vars.get(node.value) is None:
            raise Exception(f"Variable {node.value} does not exist")

        var_str = f"self.{node.value}"
        ctx.push_code(var_str)

    def visitLogicalOp(self, node: LogicalOp, ctx: Context):
        if node == LogicalOp.AND:
            op_str = "&&"
        elif node == LogicalOp.OR:
            op_str = "||"

        ctx.push_code(op_str)

    def visitCompareOp(self, node: CompareOp, ctx: Context):
        if node == CompareOp.LT:
            op_str = "<"
        else:
            raise NotImplementedError

        ctx.push_code(op_str)

    def visitSearchCondition(self, node: SearchCondition, ctx: Context):
        node.lvalue.accept(self, ctx)
        lvalue_str = ctx.pop_code()
        node.rvalue.accept(self, ctx)
        rvalue_str = ctx.pop_code()
        node.operator.accept(self, ctx)
        op_str = ctx.pop_code()

        if isinstance(node.operator, LogicalOp):
            lvalue_str = "(" + lvalue_str + ")"
            rvalue_str = "(" + rvalue_str + ")"

        cond_str = f"{lvalue_str} {op_str} {rvalue_str}"
        ctx.push_code(cond_str)
