from __future__ import annotations

import os
from typing import Any, Dict, List

import yaml

from compiler.graph import adn_base_dir
from compiler.graph.pseudo_element_compiler import pseudo_gen_property

global_element_id = 0


def fetch_global_id() -> str:
    """Assign a globally-unique id to the new element instance."""
    global global_element_id
    global_element_id += 1
    return global_element_id


class AbsElement:
    def __init__(self, edict: Dict[str, Any]):
        self.id = fetch_global_id()
        self.name: List[str] = [edict["name"]]
        self.spec: List[str] = [edict["spec"]]
        self.config = edict["config"]
        self.position = [edict["position"]]

    @property
    def desc(self) -> str:
        return "_".join(self.name) + "_" + str(self.id)

    @property
    def deploy_name(self) -> str:
        return "".join(self.name)

    @property
    def lib_name(self) -> str:
        names = [sname.split("/")[-1].split(".")[0] for sname in self.spec]
        return "_".join(names)

    @property
    def configs(self) -> str:
        return "\n".join(self.config)

    def __str__(self):
        return "+".join(self.name)

    def gen_property(self, pseudo: bool):
        """Generate properties of the element.

        Args:
            pseudo: If true, call the pseudo element compiler to generate properties.
        """
        if pseudo:
            self.property = pseudo_gen_property(self)
        else:
            self.property: Dict[str, Dict[str, Any]] = {
                "request": dict(),
                "response": dict(),
            }
            # TODO: call element compiler to generate properties
        if pseudo:
            # read handwritten properties
            for spec in self.spec:
                filename = spec.split("/")[-1].replace("sql", "yaml")
                with open(
                    os.path.join(adn_base_dir, "elements/property", filename), "r"
                ) as f:
                    current_dict = yaml.safe_load(f)
                for t in ["request", "response"]:
                    if current_dict[t] is not None:
                        for p, value in current_dict[t].items():
                            if p not in self.property[t]:
                                self.property[t][p] = value
                            elif type(value) == list:
                                self.property[t][p].extend(value)
        else:
            pass

    def fuse(self, other: AbsElement):
        """Fuse another element in

        Args:
            other: the element to be fused.
        """
        self.name.extend(other.name)
        self.spec.extend(other.spec)
        self.config.extend(other.config)
        self.position.extend(other.position)
        # TODO: fuse properties
