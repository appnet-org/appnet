"""
Module that defines the base type of visitor.
"""


from __future__ import annotations

from typing import Callable, List, Protocol, Sequence, TypeVar, Optional

from codegen.codegen import init_ctx
from codegen.context import *
from codegen.snippet import *
from tree.node import *
from tree.node import ColumnValue, InsertSelectStatement, InsertValueStatement, SelectStatement
from tree.visitor import Visitor


class RustTypeGenerator(Visitor):
    def visitNumberValue(self, node: NumberValue, ctx=None) -> RustType:
        return RustBasicType("f32", node.value)
    
    def visitStringValue(self, node: StringValue, ctx=None) -> RustType:
        val = node.value.replace("\'", "")
        return RustBasicType("String", f"String::from(\"{val}\")")

class CodeGenerator(Visitor):
    def __init__(self):
        super().__init__()
        self.type_generator = RustTypeGenerator()

    def visitRoot(self, node: List[Statement], ctx: Context) -> None:
        for statement in node:
            try:
                statement.accept(self, ctx)
            except Exception as e:
                print(statement)
                raise e

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
        table_from = node.from_table
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
            vec_from = table_from_name
        elif table_from_name == "input":
            # TODO test protobuf
            columns = [input_mapping(i) for i in columns]
            columns = ", ".join(columns)
            vec_from = table_from_name
        else:
            columns = [f"req.{i.cname}.clone()" for i in columns]
            columns = ", ".join(columns).replace(
                "req.CURRENT_TIMESTAMP.clone()", "Utc::now()"
            )
            vec_from = ctx.rust_vars[table_from_name].name

        if vec_from != "input" and vec_from != "output":
            vec_from = f"self.{vec_from}"

        if node.to_table == "":
            struct = table_from.struct
        else:
            table_to_name = node.to_table
            if ctx.tables.get(table_to_name) is None:
                raise ValueError("Table does not exist")
            table_to = ctx.tables[table_to_name]
            struct = table_to.struct

        result_rpc = f"{struct.name}::new({columns})"
        
        if ctx.is_forward:
            send_logic = """let raw_ptr: *const hello::HelloRequest = rpc_message;
                                        let new_msg = RpcMessageTx {
                                            meta_buf_ptr: req.meta_buf_ptr.clone(),
                                            addr_backend: raw_ptr.addr(),
                                        };
                                        RpcMessageGeneral::TxMessage(EngineTxMessage::RpcMessage(
                                            new_msg,
                                        ))"""
        else:
            send_logic = result_rpc

        prelude ="""let rpc_message = materialize_nocopy(&req);
            let conn_id = unsafe { &*req.meta_buf_ptr.as_meta_ptr() }.conn_id;
            let call_id = unsafe { &*req.meta_buf_ptr.as_meta_ptr() }.call_id;
            let rpc_id = RpcId::new(conn_id, call_id);"""

        drop_logic = f"let error = EngineRxMessage::Ack(rpc_id, TransportStatus::Error(unsafe {{NonZeroU32::new_unchecked(403)}}),); RpcMessageGeneral::RxMessage(error)"
        break_logic = "RpcMessageGeneral::Pass"
        
        where = node.where_clause
        join = node.join_clause
        
        ctx.name_mapping["rpc"] = "rpc_message"
        ctx.name_mapping[table_from_name] = "req"

        if join is not None:
            
            table_join = join.table_name
            if ctx.tables.get(table_join) is None:
                raise ValueError("Table does not exist")
            vec_join = ctx.rust_vars[table_join].name
            
            if vec_join != "input" and vec_join != "output":
                vec_join = f"self.{vec_join}"
            
            ctx.name_mapping[table_join] = "join"
            
            join.search_condition.accept(self, ctx)
            
            
            join_str = ctx.pop_code()

            # TODO! this is correct only if join is over all input rpcs, 
            # TODO! further check is needed for other cases
            if where is not None:
                where.search_condition.accept(self, ctx)
                where_str = ctx.pop_code()    
                send_logic = f"if ({where_str}) {{ {send_logic} }} else {{ {drop_logic} }}"
                send_logic = f"if ({join_str}) {{ {send_logic} }} else {{ {break_logic} }}"
            else:
                send_logic = f"if ({join_str}) {{ {send_logic} }} else {{ {break_logic} }}"
            
            ctx.name_mapping.pop(table_join)

            code = f"iproduct!({vec_from}.iter(), {vec_join}.iter()).map(|(req, join)| {{ {prelude} {send_logic} }}).collect()"
        else:

            if where is not None:
                where.search_condition.accept(self, ctx)
                where_str = ctx.pop_code()
                send_logic = f"if ({where_str}) {{ {send_logic} }} else {{ {drop_logic} }}"
            else:
                pass
            code = f"{vec_from}.iter().map(|req| {{ {prelude} {send_logic} }}).collect()"

        ctx.name_mapping.pop("rpc")
        ctx.name_mapping.pop(table_from_name)
        code = code
        ctx.push_code(code)

    def visitInsertValueStatement(self, node: InsertValueStatement, ctx: Context):
        table_name = node.table_name

        table = ctx.tables.get(table_name)
        if table is None:
            raise ValueError("Table does not exist")

        var_name = ctx.rust_vars[table_name].name
        
        if var_name != "output" and ctx.current == "process":
            var_name = f"self.{var_name}"
            
        struct = table.struct
        
        fields = struct.fields
        fields = [i[0] for i in fields]
        
        columns = [i.column_name for i in node.columns]
        values: List[List[RustBasicType]] = [[j.accept(self.type_generator) for j in i] for i in node.values]
        
        code = ""
        for value in values:
            v = [i.gen_init() for i in value]
            constructor = ""
            for k, v in zip(columns, v):
                constructor += f"{k}: {v}, "
            code += f"{var_name}.push({struct.name}{{{constructor}}});\n"
        
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

    def visitColumnValue(self, node: ColumnValue, ctx: Context):
        tname, cname = node.table_name, node.column_name
        if ctx.tables.get(tname) is None:
            raise Exception(f"Table {tname} does not exist")
        struct = ctx.tables[tname].struct
        fields = struct.fields
        if tname == "input":
            #todo also check meta fields
            input_name = ctx.name_mapping["rpc"]
            for msg in ctx.proto.msg:
                #todo add info for msg type
                for field in msg.fields:
                    if field == cname:
                        right = ctx.proto.msg_field_readonly(msg.name, field, input_name)
                        ctx.push_code(right) 
                        return 
        else:
            right = cname
            if cname not in [i[0] for i in fields]:
                raise Exception(f"Column {cname} does not exist in table {tname}")

        if ctx.name_mapping.get(tname) is not None:
            left = ctx.name_mapping[tname]
        else:
            table_var: RustVariable = ctx.rust_vars[tname]
            left = f"self.{table_var.name}"
            
        ctx.push_code(f"{left}.{right}")
    
    def visitStringValue(self, node: StringValue, ctx: Context):
        code = node.value.replace("\'", "")
        ctx.push_code(f"String::from(\"{code}\")")
        
    def visitLogicalOp(self, node: LogicalOp, ctx: Context):
        if node == LogicalOp.AND:
            op_str = "&&"
        elif node == LogicalOp.OR:
            op_str = "||"
        else:
            raise NotImplementedError
        ctx.push_code(op_str)

    def visitCompareOp(self, node: CompareOp, ctx: Context):
        if node == CompareOp.EQ:
            op_str = "=="
        elif node == CompareOp.NE:
            op_str = "!="
        elif node == CompareOp.LT:
            op_str = "<"
        elif node == CompareOp.LE:
            op_str = "<="
        elif node == CompareOp.GT:
            op_str = ">"
        elif node == CompareOp.GE:
            op_str = ">="   
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
