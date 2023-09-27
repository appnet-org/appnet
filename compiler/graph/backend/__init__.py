from __future__ import annotations

from typing import List, Tuple

from compiler.graph.backend.boilerplate import *
from compiler.graph.graphir.element import AbsElement


def gen_attach_detach(
    req_chain: List[AbsElement], res_chain: List[AbsElement], backend: str
):
    pre, nxt = "MrpcEngine", "TcpAdapterEngine"
    for element in chain:
        pass
        # TODO: compute prev, nxt
        # TODO: discuss whether non-linear structures are reasonable
