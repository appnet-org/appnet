from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import List, Tuple, Union, Optional

class Node:
    def __init__(self):
        pass

    def __str__(self):
        return self.__class__.__name__

    def accept(self, visitor, ctx=None):
        class_list = type(self).__mro__
        for cls in class_list:
            func_name = "visit" + cls.__name__
            visit_func = getattr(visitor, func_name, None)
            if visit_func is not None:
                return visit_func(self, ctx)
        raise Exception(f"visit function for {self.__class__.__name__} not implemented")
    
    
class Program(Node):
    def __init__(self, definition: Internal, init: Procedure, req: Procedure, resp: Procedure):
        self.definition = definition
        self.init = init
        self.req = req
        self.resp = resp
        
    
class Internal(Node):
    def __init__(self, internal: List[Tuple[Identifier, Type]]):
        self.internal = internal
    
class Procedure(Node):
    def __init__(self, name: str, params: List[Identifier], body: List[Statement]):
        self.name = name
        self.params = params
        self.body = body
    
class Statement(Node):   
    def __init__(self, stmt: Optional[Union[Match, Assign, Send, Expr]] = None):
        self.stmt = stmt
        

class Match(Statement):
    def __init__(self, match: Expr, actions: List[Tuple[Pattern, List[Statement]]]):
        self.expr = match
        self.actions = actions
    
class Assign(Statement):    
    def __init__(self, left: Identifier, right: Expr):
        self.left = left
        self.right = right

class Pattern(Node):
    def __init__(self, value: Union[Identifier, Literal, Error]):
        self.value = value

class Expr(Node):
    def __init__(self, lhs: Expr, op: Operator, rhs: Expr):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

class Identifier(Node):
    def __init__(self, name: str):
        self.name = name

class Error(Node):
    def __init__(self, msg: str):
        self.msg = msg

class FuncCall(Expr):
    def __init__(self, name: Identifier, args: List[Expr]):
        self.name = name
        self.args = args
    
class MethodCall(Expr):
    def __init__(self, obj: Identifier , method: MethodType, args: List[Expr]):
        self.obj = obj
        self.method = method
        self.args = args
        
class Send(Statement):
    def __init__(self, direction: str, msg: Expr):
        self.direction = direction
        self.msg = msg

class Type(Node):
    def __init__(self, name: str):
        self.name = name
    
class Literal(Node):
    def __init__(self, value: str):
        self.value = value
        self.type = DataType.NONE

class Start(Node):
    def __init__(self):
        pass
    
class End(Node):
    def __init__(self):
        pass

START_NODE = Start()
END_NODE = End()
PASS_NODE = Statement()

class EnumNode(Enum):
    def accept(self, visitor, ctx):
        class_list = type(self).__mro__
        for cls in class_list:
            func_name = "visit" + cls.__name__
            visit_func = getattr(visitor, func_name, None)
            if visit_func is not None:
                return visit_func(self, ctx)
        raise Exception(f"visit function for {self.name} not implemented")
    
class Operator(EnumNode):
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    EQ = 5
    NEQ = 6
    LEQ = 7
    GEQ = 8
    LE = 9
    GE = 10
    LOR = 11
    LAND = 12
    OR = 13  # bitwise
    AND = 14 # bitwise 
    XOR = 15 # bitwise
    
class DataType(EnumNode):
    INT = 1
    FLOAT = 2
    STR = 3
    BOOL = 4
    NONE = 5
    BYTE = 6
    
class MethodType(EnumNode):
    GET = 1
    SET = 2
    DELETE = 3
    SIZE = 4
    LEN = 5
    FOR_EACH = 6

class ContainerType(EnumNode):
    VEC = 1
    MAP = 2