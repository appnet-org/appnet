from lark import Transformer
from ir.node import *

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
        i = i[0]
        return i
    
    def type_(self, t):
        return t
    
    def data_type(self, d):
        d = d[0]
        return d
    
    def procedure(self, p):
        return p
    
    def name(self, n):
        n = n[0]
        return n
    
    def parameters(self, p):
        ret = []
        for i in p:
            if i != None:
                ret.append(i)
        return ret
    
    def parameter(self, p):
        if len(p) == 1:
            return p[0]
        else:
            return None
    
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
        c = c[0]
        return c
    
    def get(self, g):
        return g
    
    def set_(self, s):
        return s
    
    def delete(self, d):
        return d
    
    def op(self, o):
        o = o[0]
        return o
    
    def quoted_string(self, s):
        s = s[0]
        return s
    
    def CNAME(self, c):
        return c.value
    