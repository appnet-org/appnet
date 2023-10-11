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

    def accept(self, visitor, ctx=None):
        class_list = type(self).__mro__
        for cls in class_list:
            func_name = "visit" + cls.__name__
            visit_func = getattr(visitor, func_name, None)
            if visit_func is not None:
                return visit_func(self, ctx)
        raise Exception(f"visit function for {self.name} not implemented")
    
    
class Program(Node):
    
class Internal(Node):
    
class Procedure(Node):
    
class Statement(Node):   

class Match(Statement):
    
class Assign(Statement):    
    
class Pattern(Node):

class Expr(Node):

class Identifier(Node):
    
class FuncCall(Node):
    
class MethodCall(Node):
    
    
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
    OR = 11  # bitwise
    AND = 12 # bitwise 
    XOR = 13 # bitwise
    
class DataType(EnumNode):
    INT = 1
    FLOAT = 2
    STR = 3
    BOOL = 4
    NONE = 5
    BYTE = 6
    
    