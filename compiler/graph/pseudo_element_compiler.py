"""
The file implements a pseudo element compiler supporting
* For elements existing in the original mrpc repository, the pseudo-compiler
will copy the source code into the "{gen_dir}{engine_name}" directory.
* For elements with manually-written property file, the pseudo compiler will
load properties from file and return a python dictionary.
"""
from __future__ import annotations

import os
from typing import Any, Dict

import yaml

from compiler.graph import adn_base_dir

support_list = ["logging", "qos", "null", "ratelimit", "hotel-acl"]


def pseudo_gen_property(element) -> Dict[str, Dict[str, Any]]:
    """Generate element properties by looking up the property file list.

    Args:
        element: An AbsElement object

    Returns:
        A dictionary containing element properties on the request/response chain.
    """
    property = {"request": dict(), "response": dict()}
    for spec in element.spec:
        filename = spec.split("/")[-1].replace("sql", "yaml")
        property_file = os.path.join(adn_base_dir, "elements/property", filename)
        assert os.path.isfile(property_file), f"property file for {spec} not exist"
        with open(property_file, "r") as f:
            current_dict = yaml.safe_load(f)
        for t in ["request", "response"]:
            if current_dict[t] is not None:
                for p, value in current_dict[t].items():
                    if p not in property[t]:
                        property[t][p] = value
                    elif type(value) == list:
                        property[t][p].extend(value)
    return property


def pseudo_compile(spec: str, gen_dir: str, backend: str):
    """Generate element implementation by copying existing source code to the target path.

    Args:
        spec: Path to user specification file.
        gen_dir: Target path of implementation.
        backend: Backend name.
    """
    assert backend in ["mrpc"], f"backend {backend} not supported"
    ename = spec.split("/")[-1].split(".")[0]
    assert ename in support_list, f"element {ename} not supported"

    if backend == "mrpc":
        phoenix_dir = os.getenv("PHOENIX_DIR")
        assert phoenix_dir is not None, "environment variable PHOENIX_DIR not set"
        os.system(f"mkdir -p {gen_dir}/{ename}_mrpc/api")
        os.system(
            f"cp -Tr {phoenix_dir}/experimental/mrpc/phoenix-api/policy/{ename} {gen_dir}/{ename}_mrpc/api/{ename}"
        )
        os.system(f"mkdir -p {gen_dir}/{ename}_mrpc/plugin")
        os.system(
            f"cp -Tr {phoenix_dir}/experimental/mrpc/plugin/policy/{ename} {gen_dir}/{ename}_mrpc/plugin/{ename}"
        )
