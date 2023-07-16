from typing import Dict, List, Optional, Set, Tuple, Union

from compiler.graph.element import Element
from compiler.protobuf import Proto


class Graph:
    def __init__(self, nodes: List[Element], edges: List[Tuple[str, str]]):
        self.nodes = {node.name: node for node in nodes}
        self.edges = edges
        self._build_graph()

        self.root = self._root()
        assert len(self.root) == 1
        self.root = self.root[0]
        self.node_ordered = [i for i in self]

    def _build_graph(self):
        for edge in self.edges:
            src = self.nodes[edge[0]]
            dst = self.nodes[edge[1]]
            src.next.append(dst)
            dst.prev.append(src)

    def _root(self):
        return [node for node in self.nodes.values() if not node.prev]

    def __iter__(self):
        queue = [self.root]
        while len(queue) > 0:
            node = queue.pop(0)
            yield node
            queue.extend(node.next)

    def gen_toml(self) -> Dict[str, object]:
        # todo: This only works for linear graph
        ret = {}
        prev = "Mrpc"
        next = "TcpRpcAdapter"
        current_group = [prev, next]
        for i in self.node_ordered:
            name = i.name.split("_")
            name = [i[0].upper() + i[1:] for i in name]
            name = "".join(name)
            ret[i.name] = {
                "Me": name,
                "Prev": prev,
                "Next": next,
                "Group": str(current_group),
            }
            prev = name
            current_group = current_group[:-1] + [prev] + current_group[-1:]
        # print(ret)
        return ret
