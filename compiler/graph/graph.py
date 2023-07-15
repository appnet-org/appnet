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
