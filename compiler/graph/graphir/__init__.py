from __future__ import annotations

from typing import Any, Dict, List

from compiler.graph.graphir.element import AbsElement


class GraphIR:
    def __init__(
        self, client: str, server: str, chain: List[Dict], pair: List[Dict], type: str
    ):
        assert type in ["request", "response"], "invalid type"
        self.client = client
        self.server = server
        self.type = type
        self.client_elements: List[AbsElement] = []
        self.server_elements: List[AbsElement] = []
        # determine an initial client-server boundary
        # principle:
        # - valid ("C" goes to client, "S" goes to server)
        # - balanced #element on c/s sides
        c_id, s_id = 0, len(chain)
        for i, element in enumerate(chain):
            if element["position"] == "C":
                c_id = max(c_id, i)
            elif element["position"] == "S":
                s_id = min(s_id, i)
        assert c_id <= s_id, "invalid client/server position requirements"
        c_pt, s_pt = 0, len(chain) - 1
        while c_pt <= s_pt:
            if c_pt <= c_id:
                self.client_elements.append(AbsElement(chain[c_pt]))
                c_pt += 1
            elif s_pt >= s_id:
                self.server_elements.insert(0, AbsElement(chain[s_pt]))
                s_pt -= 1
            elif len(self.client_elements) <= len(self.server_elements):
                self.client_elements.append(AbsElement(chain[c_pt]))
                c_pt += 1
            else:
                self.server_elements.insert(0, AbsElement(chain[s_pt]))
                s_pt -= 1
        # add element pairs to c/s sides
        for pdict in pair:
            p1, p2 = ("C", "S") if type == "request" else ("S", "C")
            edict1 = {"func": pdict["func1"], "config": pdict["func1"], "position": p1}
            edict2 = {"func": pdict["func2"], "config": pdict["func2"], "position": p2}
            self.client_elements.append(AbsElement(edict1))
            self.server_elements.insert(0, AbsElement(edict2))

    def __str__(self):
        s = f"{self.client}->{self.server} {self.type} GraphIR:\n"
        s += " -> ".join(map(str, self.client_elements))
        s += " (network) "
        s += " -> ".join(map(str, self.server_elements))
        return s
