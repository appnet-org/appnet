from __future__ import annotations

from typing import Any, Dict

global_element_id = 0


def fetch_global_id() -> str:
    global global_element_id
    global_element_id += 1
    return "Element" + str(global_element_id)


class AbsElement:
    def __init__(self, edict: Dict[str, Any]):
        self.id = fetch_global_id()
        self.func = edict["func"]
        self.config = edict["config"]
        self.position = edict["position"]

    def __str__(self):
        return self.func
