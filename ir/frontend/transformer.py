from lark import Transformer


class IRTransformer(Transformer):
    def __init__(self):
        pass
    
    def start(self, n):
        return n
   
    def definition(self, d):
        return d
   
    def declaration(self, d):
        return d
   
    def identifier(self, i):
        return i
    
    def type_(self, t):
        return t
    
    def data_type(self, d):
        return d
    
    def procedure(self, p):
        return p
    
    def name(self, n):
        return n
    
    def parameters(self, p):
        return p
    
    def parameter(self, p):
        return p
    
    def body(self, b):
        return b
    
    def stage(self, s):
        return s
    
    def statement(self, s):
        return s
    
    def match(self, m):
        return m
    
    def action(self, a):
        return a
    
    def pattern(self, p):
        return p
    
    def expr(self, e):
        return e
    
    def method(self, m):
        return m
    
    def func(self, f):
        return f
    
    def const(self, c):
        return c
    
    def get(self, g):
        return g
    
    def set_(self, s):
        return s
    
    def delete(self, d):
        return d
    
    def op(self, o):
        return o