from __future__ import annotations

from copy import deepcopy
from typing import Dict, Tuple

import yaml

from compiler.graph.ir import GraphIR


class GCParser:
    def __init__(self):
        self.services = set()
        self.app_edges = []

    def parse(self, spec_path: str) -> Tuple[Dict[str, GraphIR], Dict[str, str]]:
        """Parse the user specification file and produce graphirs & service locations.

        Args:
            spec_path: Path to the user specification file.

        Returns:
            * A dictionary mapping edge name to corresponding graphir.
            * A dictionray mapping service name to hostname.
        """
        with open(spec_path, "r") as f:
            spec_dict = yaml.safe_load(f)
        for edge in spec_dict["app_structure"]:
            client, server = edge.split("->")
            client, server = client.strip(), server.strip()
            self.services.add(client)
            self.services.add(server)
            self.app_edges.append((client, server))
        graphir: Dict[str, GraphIR] = dict()
        for client, server in self.app_edges:
            chain, pair, eid = [], [], f"{client}->{server}"
            # client's egress
            if "egress" in spec_dict and client in spec_dict["egress"]:
                chain.extend(spec_dict["egress"][client])
            # client->server edge
            if "edge" in spec_dict and f"{client}->{server}" in spec_dict["edge"]:
                chain.extend(spec_dict["edge"][eid])
            # server's ingress
            if "ingress" in spec_dict and server in spec_dict["ingress"]:
                chain.extend(spec_dict["ingress"][server])
            # client->server link
            if "link" in spec_dict and f"{client}->{server}" in spec_dict["link"]:
                pair.extend(spec_dict["link"][eid])
            if len(chain) + len(pair) > 0:
                graphir[eid] = GraphIR(client, server, chain, pair)
        return graphir, spec_dict["service_pos"]
