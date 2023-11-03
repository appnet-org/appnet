from __future__ import annotations

import importlib
from typing import Dict

from compiler.graph.graphir import GraphIR


def scriptgen(girs: Dict[str, GraphIR], backend: str, service_pos: Dict[str, str]):
    try:
        module = importlib.import_module(f"compiler.graph.backend.{backend}")
    except:
        raise ValueError(f"backend {backend} not supported")
    generator = getattr(module, f"scriptgen_{backend}")
    generator(girs, service_pos)
