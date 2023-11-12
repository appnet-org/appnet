from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from compiler.graph.ir.element import AbsElement


class GraphIR:
    def __init__(self, client: str, server: str, chain: List[Dict], pair: List[Dict]):
        """Initiate an unoptimized graphir according to the specified elements.

        Args:
            client: Client service name.
            server: Server service name.
            chain: A list of dictionaries including user-specified element configs.
            pair: A list of dictionaries including user-specified paired-element configs.
                  Pair elements are deployed on the client and server sides which cancel
                  out each other.
        """
        self.client = client
        self.server = server
        self.elements: Dict[str, List[AbsElement]] = {
            "req_client": [],
            "req_server": [],
            "res_client": [],
            "res_server": [],
        }
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
                self.elements["req_client"].append(AbsElement(chain[c_pt]))
                c_pt += 1
            elif s_pt >= s_id:
                self.elements["req_server"].insert(0, AbsElement(chain[s_pt]))
                s_pt -= 1
            elif len(self.elements["req_client"]) <= len(self.elements["req_server"]):
                self.elements["req_client"].append(AbsElement(chain[c_pt]))
                c_pt += 1
            else:
                self.elements["req_server"].insert(0, AbsElement(chain[s_pt]))
                s_pt -= 1
        # The initial response graph is identical to the request graph, except for
        # the required positions of element pairs
        self.elements["res_client"] = deepcopy(self.elements["req_client"])
        self.elements["res_server"] = deepcopy(self.elements["req_server"])
        # add element pairs to c/s sides
        for pdict in pair:
            edict1 = {
                "name": "-".join([pdict["name1"], pdict["name2"]]),
                "spec": pdict["spec"],
                "config": pdict["config"],
                "position": "C",
            }
            edict2 = {
                "name": "-".join([pdict["name2"], pdict["name1"]]),
                "spec": pdict["spec"],
                "config": pdict["config"],
                "position": "S",
            }
            self.elements["req_client"].append(AbsElement(edict1))
            self.elements["req_server"].insert(0, AbsElement(edict2))
            edict1["position"], edict2["position"] = (
                edict2["position"],
                edict1["position"],
            )
            self.elements["res_client"].append(AbsElement(edict2))
            self.elements["res_server"].insert(0, AbsElement(edict1))

    def __str__(self):
        s = f"{self.client}->{self.server} request GraphIR:\n"
        s += " -> ".join(map(str, self.elements["req_client"]))
        s += " (network) "
        s += " -> ".join(map(str, self.elements["req_server"]))
        return s

    def optimize(self, pseudo: bool):
        """Run optimization algorithm on the graphir.

        Args:
            pseudo: If true, use the pseodo element compiler to generate element properties.
        """
        for chain_name in ["req_client", "res_client", "req_server", "res_server"]:
            for element in self.elements[chain_name]:
                element.gen_property(pseudo)
        # TODO: optimization algorithm
