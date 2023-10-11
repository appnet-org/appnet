from lark import Transformer


class IRTransformer(Transformer):
    def __init__(self):
        self.ir = GraphIR()

    def svalue(self, slist: list):
        return [s.value for s in slist]

    def spname(self, s):
        return s[0].value

    def string_property(self, s):
        spname, svalue = s
        return {spname: svalue}

    def true_value(self, *args):
        return True

    def false_value(self, *args):
        return False

    def bpname(self, b):
        return b[0].value

    def bool_property(self, b):
        bpname, bvalue = b
        return {bpname: bvalue}

    def properties(self, plist):
        property = dict()
        for p in plist:
            property.update(p)
        return property

    def config_name(self, c):
        return c[0].value

    def config_value(self, c):
        return c[0].value

    def config(self, c):
        cname, cvalue = c
        return {cname: cvalue}

    def configs(self, clist):
        config = dict()
        for c in clist:
            config.update(c)
        return config

    def element_name(self, e):
        return e[0].value

    def declaration(self, d):
        ename, config, property = d
        self.graph.add_element(ename, config, property)

    def order(self, o):
        e1, e2 = o
        assert self.graph.contain(e1), f"{e1} not defined"
        assert self.graph.contain(e2), f"{e2} not defined"
        self.graph.add_edge(e1, e2)

    def graphspec(self, g):
        return self.graph
