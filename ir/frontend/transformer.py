from lark import Transformer
from ir.node import *

class IRTransformer(Transformer):
    def __init__(self):
        pass
    
    def start(self, n):
        assert(len(n) == 4)
        return Program(n[0], n[1], n[2], n[3])
   
    def definition(self, d) -> Internal:
        return Internal(d)
   
    def declaration(self, d) -> Tuple[Identifier, Type]:
        return (d[0], d[1])
   
    def identifier(self, i) -> Identifier:
        i = i[0]
        return Identifier(i)
    
    def type_(self, t):
        t = t[0]
        return t
    
    def vec_type(self, t) -> Type:
        return Type(f"Vec<{t[0]}>")
    
    def map_type(self, t) -> Type:
        return Type(f"Map<{t[0]}, {t[1]}>")
    
    def single_type(self, d) -> Type:
        return Type(d[0])
        # match d:
        #     case "int":   
        #         return DataType.INT
        #     case "string":
        #         return DataType.STR
        #     case "bool":
        #         return DataType.BOOL
        #     case "float":
        #         return DataType.FLOAT
        #     case _:
        #         raise Exception("Unknown data type: " + d)
    
    def procedure(self, p) -> Procedure:
        return Procedure(p[0], p[1], p[2])
    
    def name(self, n) -> str:
        n = n[0]
        return n
    
    def parameters(self, p) -> List[Identifier]:
        ret = []
        for i in p:
            if i != None:
                ret.append(i)
        return ret
    
    def parameter(self, p) -> str:
        if len(p) == 1:
            return p[0]
        else:
            return None
    
    def body(self, b) -> List[Statement]:
        return b
    
    def stage(self, s) -> Union[Match, Statement]:
        return s[0]
    
    def statement(self, s):
        if isinstance(s[0], Statement):
            return s[0]
        else:
            return Statement(s[0])
    
    def assign(self, a) -> Assign:
        return Assign(a[0], a[1])
    
    def match(self, m) -> Match:
        return Match(m[0], m[1:])
    
    def action(self, a) -> Tuple[Pattern, List[Statement]]:
        p = a[0]
        return (p, a[1:])
    
    def pattern(self, p) -> Pattern:
        return Pattern(p[0])
    
    def some_pattern(self, p) -> Pattern:
        return Pattern(p[0])
    
    def expr(self, e) -> Expr:
        if len(e) == 1:
            return e[0]
        elif len(e) == 3:
            return Expr(e[0], e[1], e[2])
        else:
            raise Exception("Invalid expression: " + str(e))
    
    def method(self, m) -> MethodCall:
        return MethodCall(m[0], m[1][0], m[1][1])
    
    def func(self, f) -> FuncCall:
        # todo! check function name is valid
        # todo! change send to Send primitive
        # ! maybe we should have a global function list first
        assert(len(f) == 2)
        assert(isinstance(f[0], Identifier))
        if f[0].name == "send":
            assert(len(f[1]) == 2)
            assert(f[1][1].name == "APP" or f[1][1].name == "NET")
            # f[1][1] should be str, but it will be parsed as Identifier
            return Send(f[1][1].name, f[1][0])
        elif f[0].name == "err":
            assert(len(f[1]) == 1)
            return Error(f[1][0])
        else:
            return FuncCall(f[0], f[1])
    
    def arguments(self, a) -> List[Expr]:
        return a
    
    def const(self, c) -> Literal:
        c = c[0]
        return Literal(c)
    
    def err(self, e) -> Error:
        e = e[0]
        return Error(e)
    
    def get(self, g):
        return MethodType.GET, g
    
    def set_(self, s):
        return MethodType.SET, s
    
    def delete(self, d):
        return MethodType.DELETE, d
    
    def size(self, s):
        return MethodType.SIZE, []
    
    def len_(self, l):
        return MethodType.LEN, []
    
    def op(self, o) -> Operator:
        return o[0]
    
    def op_add(self, o):
        return Operator.ADD
    
    def op_sub(self, o):
        return Operator.SUB
    
    def op_mul(self, o):
        return Operator.MUL
    
    def op_div(self, o):
        return Operator.DIV
    
    def op_lor(self, o):
        return Operator.LOR
    
    def op_land(self, o):
        return Operator.LAND
    
    def op_eq(self, o):
        return Operator.EQ
    
    def op_neq(self, o):
        return Operator.NEQ
    
    def op_le(self, o):
        return Operator.LE
    
    def op_ge(self, o):
        return Operator.GE
    
    def quoted_string(self, s):
        s = s[0]
        return str(s)
    
    def CNAME(self, c):
        return c.value

    