from __future__ import annotations

import importlib
from typing import Dict

from compiler.graph.ir import GraphIR


def scriptgen(girs: Dict[str, GraphIR], backend: str, service_pos: Dict[str, str]):
    """
    Call corresponding scripg generation procedure according to the backend name.

    Args:
        girs: A dictionary mapping edge name to corresponding graphir.
        backend: backend name.
        service_pos: A dictionary mapping service name to hostname.
    """
    try:
        module = importlib.import_module(f"compiler.graph.backend.{backend}")
    except:
        raise ValueError(f"backend {backend} not supported")
    generator = getattr(module, f"scriptgen_{backend}")
    generator(girs, service_pos)
