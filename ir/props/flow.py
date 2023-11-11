from typing import Callable, List, Protocol, Sequence, TypeVar, Dict, Tuple, Optional
from ir.node import *
from ir.visitor import Visitor

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
        expr_v = Vertex(match.expr, len(self.vertices), "match_expr")
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
            
    def analyze(self, proc: Procedure) -> List[List[Statement]]:
        self.build_graph(proc)
        paths = self.extract_path()
        for path in paths:
            pass
            print("Path:")
            for step in path:
                print(step.annotation, step.idx)
            print("End of path")
        print("Total number of paths:", len(paths))

class WriteAnalyzer(Visitor):
    def __init__(self, targets: List[str]):
        self.targets = targets
    
    def visitBlock(self, node: List[Statement], ctx) -> bool:
        ret = False
        for s in node:
            ret = ret | s.accept(self, ctx)
        return ret
        
    def visitNode(self, node: Node, ctx):
        raise Exception("Unreachable!")

    def visitProgram(self, node: Program, ctx):
        raise Exception("Unreachable!")

    def visitInternal(self, node: Internal, ctx):
        raise Exception("Unreachable!")
    
    def visitProcedure(self, node: Procedure, ctx):
        raise Exception("Unreachable!")
    
    def visitStatement(self, node: Statement, ctx) -> bool:
        return self.visitNode(node)
    
    def visitMatch(self, node: Match, ctx) -> bool:
        ret = False
        for (p, s) in node.actions:
            ret = ret | p.accept(self, ctx)
            for st in s:
                ret = ret | st.accept(self, ctx)
        return ret
    
    def visitAssign(self, node: Assign, ctx) -> bool:
        return node.left.accept(self, ctx) | node.right.accept(self, ctx)
    
    def visitPattern(self, node: Pattern, ctx) -> bool:
        return node.value.accept(self, ctx)
    
    def visitExpr(self, node: Expr, ctx) -> bool:
        return node.lhs.accept(self, ctx) | node.rhs.accept(self, ctx)
    
    def visitIdentifier(self, node: Identifier, ctx) -> bool:
        return False
    
    def visitType(self, node: Type, ctx) -> bool: 
        return False
    
    def visitFuncCall(self, node: FuncCall, ctx) -> bool:
        ret = False
        ret |= node.name.accept(self, ctx) 
        for a in node.args:
            ret |= a.accept(self, ctx)
        return ret 
    
    def visitMethodCall(self, node: MethodCall, ctx) -> bool:
        if node.obj.name in self.targets and node.method.name == "set":
            return True
        ret = False
        for a in node.args:
            if a != None:
                ret = ret | a.accept(self, ctx) 
        return ret   
    
    def visitSend(self, node: Send, ctx) -> bool:
        return node.msg.accept(self, ctx)
    
    def visitLiteral(self, node: Literal, ctx) -> bool:
        return False
    
    def visitError(self, node: Error, ctx) -> bool:
        return False
  