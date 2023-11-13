from typing import Callable, List, Protocol, Sequence, TypeVar, Dict, Tuple, Optional
from ir.node import *
from ir.node import Expr, Identifier, MethodCall
from ir.visitor import Visitor

class Property():
    def __init__(self) -> None:
        self.drop: bool = False
        self.read: List[str] = []
        self.write: List[str] = []
    def to_yaml(self) -> str:
        self.write = list(set(self.write))
        self.read = list(set(self.read))
        ret = "    write:\n"
        for w in self.write:
            ret += f"   - {w}\n"
        ret += "    read:\n"
        for r in self.read:
            ret += f"   - {r}\n"
        ret += "    drop: " + str(self.drop) + "\n"
        return ret

class Edge():
    def __init__(self, u: int, v: int, w: Tuple[Expr, Expr] = []) -> None:
        self.u = u
        self.v = v
        self.w = w

class Vertex():
    def __init__(self, node: Node, idx: int, annotation: Optional[str] = None) -> None:
        self.node = node
        self.idx = idx
        if annotation is None:
            self.annotation = self.node.__class__.__name__
        else:
            self.annotation = "[" + annotation + "]" + self.node.__class__.__name__
             
class FlowGraph():
    def __init__(self) -> None:
        self.vertices: List[Vertex] = []
        self.edges: List[Edge] = []
        self.in_deg: Dict[int, int] = {} 
        

    def link(self, u: int, v: int, w: Tuple[Expr, Expr] = []) -> None:
        self.edges.append(Edge(u, v, w))
        if v in self.in_deg:
            self.in_deg[v] += 1
        else:
            self.in_deg[v] = 1

    def handle_block(self, block: List[Statement], prev: int) -> int:
        for s in block:
            assert(isinstance(s, Statement))
            v = Vertex(s, len(self.vertices))
            self.vertices.append(v)
            self.link(prev, v.idx)
            prev = v.idx
        return prev

    def handle_match(self, match: Match, prev: int) -> None:
        expr_v = Vertex(Statement(match.expr), len(self.vertices), "match_expr")
        self.vertices.append(expr_v)
        self.link(prev, expr_v.idx)
        prev = expr_v.idx
        
        end_points = []
        for (p, s) in match.actions:
            match len(s):
                case 0:
                    head = PASS_NODE # empty statement, do nothing
                    rest = []
                case 1:
                    head = s[0]
                    rest = []
                case _:
                    head = s[0]
                    rest = s[1:]
            head_v = Vertex(head, len(self.vertices), "match_head")
            self.vertices.append(head_v)
            self.link(prev, head_v.idx, (expr_v.node, p))
            
            if len(rest) == 0:
                end_points.append(head_v.idx)
            else:
                end_points.append(self.handle_block(rest, head_v.idx))
        
        merge_v = Vertex(PASS_NODE, len(self.vertices), "match_merge")
        self.vertices.append(merge_v)
        for ep in end_points:
            self.link(ep, merge_v.idx)
        
        return merge_v.idx
        
    def build_graph(self, proc: Procedure) -> None:
        start_v = Vertex(START_NODE, 0, "start")
        end_v = Vertex(END_NODE, 1, "end")
        self.vertices.append(start_v)
        self.vertices.append(end_v)
        prev = 0
        for body in proc.body:
            # order matters, since match is a subclass of statement
            if isinstance(body, Match):
                prev = self.handle_match(body, prev)
            elif isinstance(body, Statement):
                prev = self.handle_block([body], prev)
            else:
                raise Exception("build graph encountered: ", body.__class__.__name__)

        self.link(prev, end_v.idx)
    
    def extract_path(self) -> List[List[Vertex]]:
        q = [0]
        ret: Dict[int, List[List[Vertex]]] = {}
        ret[0] = [[self.vertices[0]]]
        while len(q) > 0:
            u = q.pop()
            for e in self.edges:
                if e.u == u:
                    v = self.vertices[e.v]
                    paths = ret[u].copy()
                    paths = [p + [v] for p in paths]
                    if e.v not in ret:
                        ret[e.v] = paths
                    else:
                        ret[e.v] = ret[e.v] + paths
                    self.in_deg[e.v] -= 1
                    if self.in_deg[e.v] == 0:
                        q.append(e.v)
        return ret[1]
            
    def analyze(self, proc: Procedure, verbose: bool = False) -> Property:
        self.build_graph(proc)
        paths = self.extract_path()
        rpc_name = f"rpc_{proc.name}"
        
        if proc.name == "req":
            direction = "NET"
        elif proc.name == "resp":
            direction = "APP"
        
        report = "Total #Path = " + str(len(paths)) + "\n"

        ret = Property()
            
        for path in paths:
            report += "\nFor path: \n     "
            report += "->".join([v.annotation for v in path if v != self.vertices[-1]])
            report += "\n\n"
            path_nodes = [v.node for v in path]
            aa = AliasAnalyzer(rpc_name)
            targets = aa.visitBlock(path_nodes, None)
            wa = WriteAnalyzer(targets)
            write = wa.visitBlock(path_nodes, None)
            if write:
                write_fields = wa.target_fields
                report += "Write: "
                for (k, v) in write_fields.items():
                    for vv in v:
                        report += f"{vv} " 
                        ret.write.append(vv[0])
                report += '\n'
            
            ra = ReadAnalyzer(targets)
            read = ra.visitBlock(path_nodes, None)
                       
            if read:
                read_fields = ra.target_fields
                report += "Read: "
                for (k, v) in read_fields.items():
                    for vv in v:
                        report += f"({vv}) " 
                        ret.read.append(vv)
                report += '\n'
            
            da = DropAnalyzer(targets, direction)
            no_drop = da.visitBlock(path_nodes, None)
            ret.drop = ret.drop or (not no_drop)
            
            report += "No Drop" if no_drop else "Possible Drop"
            report += '\n'
        if verbose:
            print(report)        
        return ret
        
        
class WriteAnalyzer(Visitor):
    def __init__(self, targets: List[str]):
        self.targets = targets
        self.target_fields: Dict[str, List[Tuple(str, str)]] = {}
        for t in targets:
            self.target_fields[t] = []
    
    def visitBlock(self, node: List[Statement], ctx) -> bool:
        ret = False
        for s in node:
            ret = s.accept(self, ctx) or ret
        return ret
        
    def visitNode(self, node: Node, ctx):
        if node == START_NODE or node == END_NODE or node == PASS_NODE:
            return
        print(node.__class__.__name__)
        raise Exception("Unreachable!")

    def visitProgram(self, node: Program, ctx):
        raise Exception("Unreachable!")

    def visitInternal(self, node: Internal, ctx):
        raise Exception("Unreachable!")
    
    def visitProcedure(self, node: Procedure, ctx):
        raise Exception("Unreachable!")
    
    def visitStatement(self, node: Statement, ctx):
        if node.stmt == None:
            return
        else:
            return node.stmt.accept(self, ctx)
    
    def visitMatch(self, node: Match, ctx) -> bool:
        ret = False
        for (p, s) in node.actions:
            ret = p.accept(self, ctx) or ret
            for st in s:
                ret = st.accept(self, ctx) or ret
        return ret
    
    def visitAssign(self, node: Assign, ctx) -> bool:
        return node.left.accept(self, ctx) or node.right.accept(self, ctx)
    
    def visitPattern(self, node: Pattern, ctx) -> bool:
        return node.value.accept(self, ctx)
    
    def visitExpr(self, node: Expr, ctx) -> bool:
        return node.lhs.accept(self, ctx) or node.rhs.accept(self, ctx)
    
    def visitIdentifier(self, node: Identifier, ctx) -> bool:
        return False
    
    def visitType(self, node: Type, ctx) -> bool: 
        return False
    
    def visitFuncCall(self, node: FuncCall, ctx) -> bool:
        ret = node.name.accept(self, ctx) 
        for a in node.args:
            ret = a.accept(self, ctx) or ret
        return ret 
    
    def visitMethodCall(self, node: MethodCall, ctx) -> bool:
        assert(isinstance(node.obj, Identifier))
        if node.obj.name in self.targets and node.method.name == "SET":
            er = ExprResolver()
            assert(len(node.args) == 2)
            fields = [i.accept(er, None) for i in node.args]
            self.target_fields[node.obj.name] += [(fields[0], fields[1])]
            return True
        ret = False
        for a in node.args:
            if a != None:
                ret = a.accept(self, ctx) or ret
        return ret   
    
    def visitSend(self, node: Send, ctx) -> bool:
        return node.msg.accept(self, ctx)
    
    def visitLiteral(self, node: Literal, ctx) -> bool:
        return False
    
    def visitError(self, node: Error, ctx) -> bool:
        return False
  
class ReadAnalyzer(Visitor):
    def __init__(self, targets: List[str]):
        self.targets = targets
        self.target_fields: Dict[str, List[str]] = {}
        for t in targets:
            self.target_fields[t] = []
            
    def visitBlock(self, node: List[Statement], ctx) -> bool:
        ret = False
        for s in node:
            ret = s.accept(self, ctx) or ret
        return ret
        
    def visitNode(self, node: Node, ctx):
        if node == START_NODE or node == END_NODE or node == PASS_NODE:
            return
        print(node.__class__.__name__)
        raise Exception("Unreachable!")

    def visitProgram(self, node: Program, ctx):
        raise Exception("Unreachable!")

    def visitInternal(self, node: Internal, ctx):
        raise Exception("Unreachable!")
    
    def visitProcedure(self, node: Procedure, ctx):
        raise Exception("Unreachable!")
    
    def visitStatement(self, node: Statement, ctx):
        if node.stmt == None:
            return
        else:
            return node.stmt.accept(self, ctx)
    
    def visitMatch(self, node: Match, ctx) -> bool:
        ret = False
        for (p, s) in node.actions:
            ret = p.accept(self, ctx) or ret
            for st in s:
                ret = st.accept(self, ctx) or ret
        return ret
    
    def visitAssign(self, node: Assign, ctx) -> bool:
        return node.left.accept(self, ctx) or node.right.accept(self, ctx)
    
    def visitPattern(self, node: Pattern, ctx) -> bool:
        return node.value.accept(self, ctx)
    
    def visitExpr(self, node: Expr, ctx) -> bool:
        return node.lhs.accept(self, ctx) or node.rhs.accept(self, ctx)
    
    def visitIdentifier(self, node: Identifier, ctx) -> bool:
        return False
    
    def visitType(self, node: Type, ctx) -> bool: 
        return False
    
    def visitFuncCall(self, node: FuncCall, ctx) -> bool:
        ret = node.name.accept(self, ctx) 
        for a in node.args:
            ret = a.accept(self, ctx) or ret
        return ret 
    
    def visitMethodCall(self, node: MethodCall, ctx) -> bool:
        if isinstance(node.obj, Identifier):
            if node.obj.name in self.targets and node.method.name == "GET":
                er = ExprResolver()
                fields = [i.accept(er, None) for i in node.args]
                self.target_fields[node.obj.name] += fields
                return True
        else:
            raise NotADirectoryError
        ret = False
        for a in node.args:
            if a != None:
                ret = a.accept(self, ctx) or ret
        return ret   
    
    def visitSend(self, node: Send, ctx) -> bool:
        return node.msg.accept(self, ctx)
    
    def visitLiteral(self, node: Literal, ctx) -> bool:
        return False
    
    def visitError(self, node: Error, ctx) -> bool:
        return False
  
class DropAnalyzer(Visitor):
    def __init__(self, targets: List[str], direction: str):
        self.direction = direction
        self.targets = targets
        self.target_fields: Dict[str, List[str]] = {}
        for t in targets:
            self.target_fields[t] = []
            
    def visitBlock(self, node: List[Statement], ctx) -> bool:
        ret = False
        for s in node:
            ret = s.accept(self, ctx) or ret
        return ret
        
    def visitNode(self, node: Node, ctx):
        if node == START_NODE or node == END_NODE or node == PASS_NODE:
            return
        print(node.__class__.__name__)
        raise Exception("Unreachable!")

    def visitProgram(self, node: Program, ctx):
        raise Exception("Unreachable!")

    def visitInternal(self, node: Internal, ctx):
        raise Exception("Unreachable!")
    
    def visitProcedure(self, node: Procedure, ctx):
        raise Exception("Unreachable!")
    
    def visitStatement(self, node: Statement, ctx):
        if node.stmt == None:
            return
        else:
            return node.stmt.accept(self, ctx)
    
    def visitMatch(self, node: Match, ctx) -> bool:
        raise Exception("Unreachable! Match should not appear in drop analyzer")
    
    def visitAssign(self, node: Assign, ctx) -> bool:
        return False
    
    def visitPattern(self, node: Pattern, ctx) -> bool:
        return False
    
    def visitExpr(self, node: Expr, ctx) -> bool:
        return node.lhs.accept(self, ctx) or node.rhs.accept(self, ctx)
    
    def visitIdentifier(self, node: Identifier, ctx) -> bool:
        return False
    
    def visitType(self, node: Type, ctx) -> bool: 
        return False
    
    def visitFuncCall(self, node: FuncCall, ctx) -> bool:
        return False
    
    def visitMethodCall(self, node: MethodCall, ctx) -> bool:
        return False  
    
    def visitSend(self, node: Send, ctx) -> bool:
        if node.direction == self.direction:
            name = node.msg.accept(ExprResolver(), ctx)
            return name in self.targets
        else:
            return False    
    def visitLiteral(self, node: Literal, ctx) -> bool:
        return False
    
    def visitError(self, node: Error, ctx) -> bool:
        return False
   
class AliasAnalyzer(Visitor):
    def __init__(self, target: str):
        self.targets: List[str] = [target]
        self.target_fields: Dict[str, List[str]] = {}
        for t in self.targets:
            self.target_fields[t] = []
            
    def visitBlock(self, node: List[Statement], ctx) -> List[str]:
        for s in node:
            s.accept(self, ctx)
        return self.targets
    
    def visitNode(self, node: Node, ctx):
        if node == START_NODE or node == END_NODE or node == PASS_NODE:
            return
        print(node.__class__.__name__)
        raise Exception("Unreachable!")

    def visitProgram(self, node: Program, ctx):
        raise Exception("Unreachable!")

    def visitInternal(self, node: Internal, ctx):
        raise Exception("Unreachable!")
    
    def visitProcedure(self, node: Procedure, ctx):
        raise Exception("Unreachable!")
    
    def visitStatement(self, node: Statement, ctx):
        if node.stmt == None:
            return
        else:
            return node.stmt.accept(self, ctx)
    
    def visitMatch(self, node: Match, ctx):
        for (p, s) in node.actions:
            p.accept(self, ctx)
            for st in s:
                st.accept(self, ctx)
    
    def visitAssign(self, node: Assign, ctx):
        name = node.left.name
        is_target = node.right.accept(self, ctx)
        if is_target == True:
             self.targets.append(name)
             self.target_fields[name] = []
    
    def visitPattern(self, node: Pattern, ctx) -> bool:
        return node.value.accept(self, ctx)
    
    def visitExpr(self, node: Expr, ctx) -> bool:
        if isinstance(node.lhs, Identifier) and node.lhs.name in self.targets:
            return True
        if isinstance(node.rhs, Identifier) and node.rhs.name in self.targets:
            return True
        return node.lhs.accept(self, ctx) or node.rhs.accept(self, ctx)
    
    def visitIdentifier(self, node: Identifier, ctx) -> str:
        return node.name in self.targets
    
    def visitType(self, node: Type, ctx) -> bool: 
        return False
    
    def visitFuncCall(self, node: FuncCall, ctx) -> bool:
        ret = node.name.accept(self, ctx) 
        for a in node.args:
            ret = a.accept(self, ctx) or ret
        return ret 
    
    def visitMethodCall(self, node: MethodCall, ctx) -> bool:
        assert(isinstance(node.obj, Identifier))
        if node.obj.name in self.targets:
            if node.method.name == "GET":
                return True
        return False
    
    def visitSend(self, node: Send, ctx) -> bool:
        return False
    
    def visitLiteral(self, node: Literal, ctx) -> bool:
        return False
    
    def visitError(self, node: Error, ctx) -> bool:
        return False
    
class ExprResolver(Visitor):
    def __init__(self) -> None:
        pass
    
    def visitNode(self, node: Node, ctx) -> str:
        print(node.__class__.__name__)
        raise Exception("Unreachable!")
    
    def visitLiteral(self, node: Literal, ctx) -> str:
        return node.value
    
    def visitIdentifier(self, node: Identifier, ctx) -> str:
        return node.name
        
    def visitExpr(self, node: Expr, ctx) -> str:
        return node.lhs.accept(self, ctx) + str(node.op) + node.rhs.accept(self, ctx)
    
    def visitMethodCall(self, node: MethodCall, ctx):
        return node.obj.accept(self, ctx) + "." + node.method.name + "(" + ",".join([a.accept(self, ctx) for a in node.args]) + ")"